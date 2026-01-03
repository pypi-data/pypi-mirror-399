from __future__ import annotations

import json
import locale as pylocale
import os
import platform
import socket
import sys
import time
import uuid
from dataclasses import replace
from pathlib import Path

from ..model import (
    CollectorResult,
    CPUInfo,
    HostIdentity,
    HostSpec,
    MemoryInfo,
    NetworkInfo,
    NetworkInterface,
    OSInfo,
    PerformanceSnapshot,
    SoftwareInfo,
    StorageInfo,
    StorageVolume,
    VirtualizationInfo,
)
from ..utils.exec import run_cmd
from ..utils.timing import timed


@timed("host_identity")
def collect_host_identity(spec: HostSpec):
    warnings: list[str] = []
    errors: list[str] = []
    sources: list[str] = []

    hostname = None
    fqdn = None
    domain = None
    machine_id = None
    tz = None
    loc = None

    try:
        hostname = socket.gethostname()
        sources.append("socket.gethostname")
    except Exception as e:
        errors.append(f"hostname: {e}")

    try:
        fqdn = socket.getfqdn() or None
        sources.append("socket.getfqdn")
    except Exception as e:
        warnings.append(f"fqdn: {e}")

    # Best-effort: infer domain/workgroup from FQDN if present.
    if fqdn and hostname and fqdn.lower().startswith(hostname.lower() + "."):
        domain = fqdn.split(".", 1)[1]

    # Best-effort machine id: uuid.getnode can be MAC-derived; treat as sensitive.
    try:
        node = uuid.getnode()
        machine_id = f"node:{node:012x}"
        sources.append("uuid.getnode")
    except Exception as e:
        warnings.append(f"machine_id: {e}")

    try:
        tz = time.tzname[0] if time.tzname else None
        sources.append("time.tzname")
    except Exception as e:
        warnings.append(f"timezone: {e}")

    try:
        loc = pylocale.getlocale()[0] or pylocale.getdefaultlocale()[0]
        sources.append("locale.getlocale/getdefaultlocale")
    except Exception as e:
        warnings.append(f"locale: {e}")

    # Uptime/boot time are best-effort; prefer psutil when available.
    boot_time_utc = None
    uptime_seconds = None

    try:
        import psutil  # type: ignore

        bt = psutil.boot_time()
        boot_time_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(bt))
        uptime_seconds = int(time.time() - bt)
        sources.append("psutil.boot_time")
    except Exception:
        # no psutil or failed; omit (do not error)
        pass

    host = HostIdentity(
        hostname=hostname,
        fqdn=fqdn,
        domain_or_workgroup=domain,
        machine_id=machine_id,
        boot_time_utc=boot_time_utc,
        uptime_seconds=uptime_seconds,
        timezone=tz,
        locale=loc,
    )

    return replace(spec, host_identity=host), CollectorResult(
        name="host_identity",
        ok=True,
        duration_ms=0,
        warnings=tuple(warnings),
        errors=tuple(errors),
        sources=tuple(sources),
    )


@timed("os")
def collect_os(spec: HostSpec):
    warnings: list[str] = []
    sources: list[str] = []

    plat = sys.platform
    if plat.startswith("win"):
        platform_key = "windows"
    elif plat.startswith("linux"):
        platform_key = "linux"
    elif plat == "darwin":
        platform_key = "darwin"
    else:
        platform_key = plat

    name = None
    version = None
    build = None
    kernel = None
    arch = None

    try:
        name = platform.system()
        version = platform.version()
        sources.append("platform.system/version")
    except Exception as e:
        warnings.append(f"platform: {e}")

    try:
        build = platform.release()
        kernel = platform.uname().release
        arch = platform.machine()
        sources.append("platform.release/uname/machine")
    except Exception as e:
        warnings.append(f"platform.uname: {e}")

    power_profile = None
    throttle_hints: list[str] = []

    # Windows power plan: best-effort via `powercfg /getactivescheme`.
    if platform_key == "windows":
        out = run_cmd(["powercfg", "/getactivescheme"], timeout=3)
        if out.ok and out.stdout:
            power_profile = out.stdout.strip()
            sources.append("powercfg /getactivescheme")
        elif out.error:
            warnings.append(f"powercfg: {out.error}")

    osinfo = OSInfo(
        platform=platform_key,
        name=name,
        version=version,
        build=build,
        kernel=kernel,
        architecture=arch,
        power_profile=power_profile,
        throttle_hints=tuple(throttle_hints),
    )

    return replace(spec, os=osinfo), CollectorResult(
        name="os",
        ok=True,
        duration_ms=0,
        warnings=tuple(warnings),
        errors=(),
        sources=tuple(sources),
    )


@timed("cpu")
def collect_cpu(spec: HostSpec):
    warnings: list[str] = []
    sources: list[str] = []

    vendor = None
    brand = None

    try:
        brand = platform.processor() or None
        sources.append("platform.processor")
    except Exception as e:
        warnings.append(f"platform.processor: {e}")

    logical = os.cpu_count()

    # `platform.processor()` is often empty on Windows; use WMIC if present.
    if sys.platform.startswith("win"):
        out = run_cmd(
            [
                "wmic",
                "cpu",
                "get",
                "Name,Manufacturer,MaxClockSpeed",
                "/format:json",
            ],
            timeout=5,
        )
        if out.ok and out.stdout:
            try:
                data = json.loads(out.stdout)
                items = data.get("value") or []
                if items:
                    vendor = items[0].get("Manufacturer") or vendor
                    brand = items[0].get("Name") or brand
                    sources.append("wmic cpu")
            except Exception as e:
                warnings.append(f"wmic cpu parse: {e}")
        elif out.error:
            warnings.append(f"wmic cpu: {out.error}")

    cpu = CPUInfo(
        vendor=vendor,
        brand=brand,
        sockets=None,
        physical_cores=None,
        logical_processors=logical,
        base_mhz=None,
        max_mhz=None,
        current_mhz=None,
        flags=(),
    )

    return replace(spec, cpu=cpu), CollectorResult(
        name="cpu",
        ok=True,
        duration_ms=0,
        warnings=tuple(warnings),
        errors=(),
        sources=tuple(sources),
    )


@timed("memory")
def collect_memory(spec: HostSpec):
    warnings: list[str] = []
    sources: list[str] = []

    total = None
    avail = None
    used = None
    swap_total = None
    swap_used = None

    try:
        import psutil  # type: ignore

        vm = psutil.virtual_memory()
        total = int(vm.total)
        avail = int(vm.available)
        used = int(vm.used)
        sources.append("psutil.virtual_memory")

        sm = psutil.swap_memory()
        swap_total = int(sm.total)
        swap_used = int(sm.used)
        sources.append("psutil.swap_memory")
    except Exception:
        # stdlib-only fallback: not uniformly available cross-platform.
        pass

    mem = MemoryInfo(
        total_bytes=total,
        available_bytes=avail,
        used_bytes=used,
        swap_total_bytes=swap_total,
        swap_used_bytes=swap_used,
        ecc=None,
    )

    return replace(spec, memory=mem), CollectorResult(
        name="memory",
        ok=True,
        duration_ms=0,
        warnings=tuple(warnings),
        errors=(),
        sources=tuple(sources),
    )


@timed("storage")
def collect_storage(spec: HostSpec):
    warnings: list[str] = []
    sources: list[str] = []

    volumes: list[StorageVolume] = []

    # Cross-platform: use shutil.disk_usage on known mountpoints; on Windows,
    # enumerate drive letters A-Z.
    try:
        import shutil

        if sys.platform.startswith("win"):
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                mount = f"{letter}:\\"
                if Path(mount).exists():
                    try:
                        du = shutil.disk_usage(mount)
                        volumes.append(
                            StorageVolume(
                                name=letter + ":",
                                mountpoint=mount,
                                fstype=None,
                                total_bytes=int(du.total),
                                used_bytes=int(du.used),
                                free_bytes=int(du.free),
                            )
                        )
                    except Exception as e:
                        warnings.append(f"disk_usage {mount}: {e}")
            sources.append("shutil.disk_usage drive letters")
        else:
            for mount in ("/", "/home", "/var"):
                try:
                    du = shutil.disk_usage(mount)
                    volumes.append(
                        StorageVolume(
                            name=mount,
                            mountpoint=mount,
                            fstype=None,
                            total_bytes=int(du.total),
                            used_bytes=int(du.used),
                            free_bytes=int(du.free),
                        )
                    )
                except Exception:
                    pass
            sources.append("shutil.disk_usage common mounts")
    except Exception as e:
        warnings.append(f"storage: {e}")

    # Deterministic ordering.
    volumes_sorted = tuple(
        sorted(volumes, key=lambda v: (v.mountpoint or "", v.name or ""))
    )

    storage = StorageInfo(volumes=volumes_sorted, encryption=None)
    return replace(spec, storage=storage), CollectorResult(
        name="storage",
        ok=True,
        duration_ms=0,
        warnings=tuple(warnings),
        errors=(),
        sources=tuple(sources),
    )


@timed("network")
def collect_network(spec: HostSpec):
    warnings: list[str] = []
    sources: list[str] = []

    interfaces: list[NetworkInterface] = []

    # Stdlib approach: getaddrinfo for local host; does not enumerate per NIC.
    try:
        host = socket.gethostname()
        infos = socket.getaddrinfo(host, None)
        ipv4: set[str] = set()
        ipv6: set[str] = set()
        for fam, _, _, _, sockaddr in infos:
            if fam == socket.AF_INET:
                ip = sockaddr[0]
                ipv4.add(ip)
            elif fam == socket.AF_INET6:
                ip = sockaddr[0]
                ipv6.add(ip)
        interfaces.append(
            NetworkInterface(
                name="host",
                ipv4=tuple(sorted(ipv4)),
                ipv6=tuple(sorted(ipv6)),
            )
        )
        sources.append("socket.getaddrinfo(hostname)")
    except Exception as e:
        warnings.append(f"getaddrinfo: {e}")

    # Windows: try `ipconfig /all` parse (best-effort, not perfect).
    if sys.platform.startswith("win"):
        out = run_cmd(["ipconfig", "/all"], timeout=5)
        if out.ok and out.stdout:
            # Keep minimal: do not try to fully parse adapter blocks.
            sources.append("ipconfig /all (unparsed)")

    # Deterministic ordering.
    iface_sorted = tuple(sorted(interfaces, key=lambda i: i.name))

    net = NetworkInfo(
        interfaces=iface_sorted,
        dns_servers=(),
        gateways=(),
        proxy=os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY"),
    )

    return replace(spec, network=net), CollectorResult(
        name="network",
        ok=True,
        duration_ms=0,
        warnings=tuple(warnings),
        errors=(),
        sources=tuple(sources),
    )


@timed("software")
def collect_software(spec: HostSpec):
    warnings: list[str] = []
    sources: list[str] = []

    python = platform.python_version()
    pyexe = sys.executable
    sources.append("platform.python_version/sys.executable")

    def version_of(cmd: list[str]) -> str | None:
        out = run_cmd(cmd, timeout=3)
        if out.ok and out.stdout:
            return out.stdout.strip().splitlines()[0]
        return None

    dotnet = version_of(["dotnet", "--info"])
    if dotnet:
        sources.append("dotnet --info")

    # `java -version` often writes to stderr; handled by run_cmd.
    java = version_of(["java", "-version"])
    if java:
        sources.append("java -version")

    node = version_of(["node", "--version"])
    if node:
        sources.append("node --version")

    docker = version_of(["docker", "--version"])
    if docker:
        sources.append("docker --version")

    openssl = version_of(["openssl", "version"])
    if openssl:
        sources.append("openssl version")

    s = SoftwareInfo(
        python=python,
        python_executable=pyexe,
        dotnet=dotnet,
        java=java,
        node=node,
        docker=docker,
        openssl=openssl,
    )

    return replace(spec, software=s), CollectorResult(
        name="software",
        ok=True,
        duration_ms=0,
        warnings=tuple(warnings),
        errors=(),
        sources=tuple(sources),
    )


@timed("virtualization")
def collect_virtualization(spec: HostSpec):
    warnings: list[str] = []
    sources: list[str] = []

    is_vm = None
    hypervisor = None
    wsl = None

    # Heuristics only, stdlib-first.
    if sys.platform.startswith("linux"):
        # Common container signals.
        try:
            if Path("/.dockerenv").exists():
                hypervisor = "docker"
                sources.append("/.dockerenv")
        except Exception:
            pass

    if sys.platform.startswith("win"):
        out = run_cmd(["wsl", "--version"], timeout=3)
        if out.ok and (out.stdout or out.stderr):
            wsl = (out.stdout or out.stderr).strip().splitlines()[0]
            sources.append("wsl --version")

    v = VirtualizationInfo(
        is_vm=is_vm,
        hypervisor=hypervisor,
        wsl=wsl,
        container_runtime=None,
        container_limits=(),
    )

    return replace(spec, virtualization=v), CollectorResult(
        name="virtualization",
        ok=True,
        duration_ms=0,
        warnings=tuple(warnings),
        errors=(),
        sources=tuple(sources),
    )


@timed("performance_snapshot")
def collect_performance_snapshot(spec: HostSpec):
    warnings: list[str] = []
    sources: list[str] = []

    cpu_percent = None
    mem_percent = None
    disk_usage_percent: list[tuple[str, float]] = []

    try:
        import psutil  # type: ignore

        cpu_percent = float(psutil.cpu_percent(interval=0.0))
        mem_percent = float(psutil.virtual_memory().percent)
        sources.append("psutil cpu_percent/virtual_memory")

        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disk_usage_percent.append((part.mountpoint, float(usage.percent)))
            except Exception:
                continue
        disk_usage_percent = sorted(disk_usage_percent, key=lambda x: x[0])
        sources.append("psutil.disk_partitions/disk_usage")
    except Exception:
        pass

    snap = PerformanceSnapshot(
        cpu_percent=cpu_percent,
        memory_percent=mem_percent,
        disk_usage_percent=tuple(disk_usage_percent),
    )

    return replace(spec, performance_snapshot=snap), CollectorResult(
        name="performance_snapshot",
        ok=True,
        duration_ms=0,
        warnings=tuple(warnings),
        errors=(),
        sources=tuple(sources),
    )
