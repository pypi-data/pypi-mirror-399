from __future__ import annotations

import json
import sys
from dataclasses import replace

from ..model import CollectorResult, FirmwareInfo, HostSpec, SecurityInfo
from ..utils.exec import run_cmd
from ..utils.timing import timed


@timed("firmware_windows")
def collect_firmware_windows(spec: HostSpec):
    warnings: list[str] = []
    sources: list[str] = []

    bios_vendor = None
    bios_version = None
    bios_date = None
    board_vendor = None
    board_model = None

    if not sys.platform.startswith("win"):
        return spec, CollectorResult(
            name="firmware_windows",
            ok=True,
            duration_ms=0,
            warnings=(),
            errors=(),
            sources=(),
        )

    # Best-effort via WMIC if present.
    out = run_cmd(
        [
            "wmic",
            "bios",
            "get",
            "Manufacturer,SMBIOSBIOSVersion,ReleaseDate",
            "/format:json",
        ],
        timeout=5,
    )
    if out.ok and out.stdout:
        try:
            data = json.loads(out.stdout)
            items = data.get("value") or []
            if items:
                bios_vendor = items[0].get("Manufacturer")
                bios_version = items[0].get("SMBIOSBIOSVersion")
                bios_date = items[0].get("ReleaseDate")
                sources.append("wmic bios")
        except Exception as e:
            warnings.append(f"wmic bios parse: {e}")

    out2 = run_cmd(
        ["wmic", "baseboard", "get", "Manufacturer,Product", "/format:json"],
        timeout=5,
    )
    if out2.ok and out2.stdout:
        try:
            data = json.loads(out2.stdout)
            items = data.get("value") or []
            if items:
                board_vendor = items[0].get("Manufacturer")
                board_model = items[0].get("Product")
                sources.append("wmic baseboard")
        except Exception as e:
            warnings.append(f"wmic baseboard parse: {e}")

    fw = FirmwareInfo(
        bios_vendor=bios_vendor,
        bios_version=bios_version,
        bios_date=bios_date,
        board_vendor=board_vendor,
        board_model=board_model,
        secure_boot_enabled=None,
        tpm_present=None,
        tpm_version=None,
    )

    return replace(spec, firmware=fw), CollectorResult(
        name="firmware_windows",
        ok=True,
        duration_ms=0,
        warnings=tuple(warnings),
        errors=(),
        sources=tuple(sources),
    )


@timed("security_windows")
def collect_security_windows(spec: HostSpec):
    warnings: list[str] = []
    sources: list[str] = []

    if not sys.platform.startswith("win"):
        return spec, CollectorResult(
            name="security_windows",
            ok=True,
            duration_ms=0,
            warnings=(),
            errors=(),
            sources=(),
        )

    firewall = None

    # Best-effort via netsh.
    out = run_cmd(["netsh", "advfirewall", "show", "allprofiles"], timeout=5)
    if out.ok and (out.stdout or out.stderr):
        firewall = (out.stdout or out.stderr).strip().splitlines()[0]
        sources.append("netsh advfirewall")

    sec = SecurityInfo(
        firewall=firewall,
        antivirus=None,
        secure_boot_enabled=spec.firmware.secure_boot_enabled,
        tpm_present=spec.firmware.tpm_present,
    )

    return replace(spec, security=sec), CollectorResult(
        name="security_windows",
        ok=True,
        duration_ms=0,
        warnings=tuple(warnings),
        errors=(),
        sources=tuple(sources),
    )
