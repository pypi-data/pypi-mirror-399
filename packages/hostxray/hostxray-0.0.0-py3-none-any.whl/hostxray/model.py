from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from .redaction import RedactionConfig

JsonPrimitive = str | int | float | bool | None
JsonValue = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(frozen=True, slots=True)
class CollectorResult:
    name: str
    ok: bool
    duration_ms: int
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    sources: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class HostIdentity:
    hostname: str | None = None
    fqdn: str | None = None
    domain_or_workgroup: str | None = None
    machine_id: str | None = None
    boot_time_utc: str | None = None
    uptime_seconds: int | None = None
    timezone: str | None = None
    locale: str | None = None


@dataclass(frozen=True, slots=True)
class OSInfo:
    platform: str | None = None  # windows|linux|darwin
    name: str | None = None
    version: str | None = None
    build: str | None = None
    kernel: str | None = None
    architecture: str | None = None
    power_profile: str | None = None
    throttle_hints: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class FirmwareInfo:
    bios_vendor: str | None = None
    bios_version: str | None = None
    bios_date: str | None = None
    board_vendor: str | None = None
    board_model: str | None = None
    secure_boot_enabled: bool | None = None
    tpm_present: bool | None = None
    tpm_version: str | None = None


@dataclass(frozen=True, slots=True)
class CPUInfo:
    vendor: str | None = None
    brand: str | None = None
    sockets: int | None = None
    physical_cores: int | None = None
    logical_processors: int | None = None
    base_mhz: int | None = None
    max_mhz: int | None = None
    current_mhz: int | None = None
    flags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class MemoryInfo:
    total_bytes: int | None = None
    available_bytes: int | None = None
    used_bytes: int | None = None
    swap_total_bytes: int | None = None
    swap_used_bytes: int | None = None
    ecc: bool | None = None


@dataclass(frozen=True, slots=True)
class GPUDevice:
    name: str | None = None
    vendor: str | None = None
    vram_total_bytes: int | None = None
    driver_version: str | None = None
    bus_id: str | None = None
    integrated: bool | None = None


@dataclass(frozen=True, slots=True)
class GPUInfo:
    devices: tuple[GPUDevice, ...] = ()
    cuda_version: str | None = None
    rocm_version: str | None = None
    directml: bool | None = None


@dataclass(frozen=True, slots=True)
class StorageVolume:
    name: str | None = None
    mountpoint: str | None = None
    fstype: str | None = None
    total_bytes: int | None = None
    used_bytes: int | None = None
    free_bytes: int | None = None


@dataclass(frozen=True, slots=True)
class StorageInfo:
    volumes: tuple[StorageVolume, ...] = ()
    encryption: str | None = None


@dataclass(frozen=True, slots=True)
class NetworkInterface:
    name: str
    mac: str | None = None
    mtu: int | None = None
    is_up: bool | None = None
    ipv4: tuple[str, ...] = ()
    ipv6: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class NetworkInfo:
    interfaces: tuple[NetworkInterface, ...] = ()
    dns_servers: tuple[str, ...] = ()
    gateways: tuple[str, ...] = ()
    proxy: str | None = None


@dataclass(frozen=True, slots=True)
class SoftwareInfo:
    python: str | None = None
    python_executable: str | None = None
    dotnet: str | None = None
    java: str | None = None
    node: str | None = None
    docker: str | None = None
    openssl: str | None = None


@dataclass(frozen=True, slots=True)
class SecurityInfo:
    firewall: str | None = None
    antivirus: str | None = None
    secure_boot_enabled: bool | None = None
    tpm_present: bool | None = None


@dataclass(frozen=True, slots=True)
class VirtualizationInfo:
    is_vm: bool | None = None
    hypervisor: str | None = None
    wsl: str | None = None
    container_runtime: str | None = None
    container_limits: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PerformanceSnapshot:
    cpu_percent: float | None = None
    memory_percent: float | None = None
    disk_usage_percent: tuple[tuple[str, float], ...] = ()


@dataclass(frozen=True, slots=True)
class CollectionMetadata:
    collected_at_utc: str = field(default_factory=_utc_now_iso)
    profile: Literal["minimal", "standard", "full"] = "standard"
    platform: str | None = None
    results: tuple[CollectorResult, ...] = ()


@dataclass(frozen=True, slots=True)
class HostSpec:
    host_identity: HostIdentity = field(default_factory=HostIdentity)
    os: OSInfo = field(default_factory=OSInfo)
    firmware: FirmwareInfo = field(default_factory=FirmwareInfo)
    cpu: CPUInfo = field(default_factory=CPUInfo)
    memory: MemoryInfo = field(default_factory=MemoryInfo)
    gpu: GPUInfo = field(default_factory=GPUInfo)
    storage: StorageInfo = field(default_factory=StorageInfo)
    network: NetworkInfo = field(default_factory=NetworkInfo)
    software: SoftwareInfo = field(default_factory=SoftwareInfo)
    security: SecurityInfo = field(default_factory=SecurityInfo)
    virtualization: VirtualizationInfo = field(default_factory=VirtualizationInfo)
    performance_snapshot: PerformanceSnapshot = field(
        default_factory=PerformanceSnapshot
    )
    collection_metadata: CollectionMetadata = field(default_factory=CollectionMetadata)
    redaction: RedactionConfig = field(default_factory=RedactionConfig)

    def to_dict(self) -> dict[str, JsonValue]:
        # `asdict` keeps deterministic field order based on dataclass definition.
        # We then normalize types to be strictly JSON-serializable.

        def jsonify(value: Any) -> JsonValue:
            if value is None or isinstance(value, (str, int, float, bool)):
                return value
            if isinstance(value, Enum):
                return str(value.value)
            if isinstance(value, dict):
                return {str(k): jsonify(v) for k, v in value.items()}
            if isinstance(value, (list, tuple)):
                return [jsonify(v) for v in value]
            if isinstance(value, set):
                # Deterministic ordering.
                return [jsonify(v) for v in sorted(value, key=lambda x: str(x))]
            # Fallback for any unexpected objects.
            return str(value)

        raw: dict[str, Any] = asdict(self)
        return jsonify(raw)  # type: ignore[return-value]

    def to_json(self, *, indent: int | None = None) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=False)

    def redacted(self) -> "HostSpec":
        from .redaction import apply_redaction

        return apply_redaction(self, self.redaction)
