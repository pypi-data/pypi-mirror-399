from __future__ import annotations

from dataclasses import replace

from .collectors.core import (
    collect_cpu,
    collect_host_identity,
    collect_memory,
    collect_network,
    collect_os,
    collect_performance_snapshot,
    collect_software,
    collect_storage,
    collect_virtualization,
)
from .collectors.windows import collect_firmware_windows, collect_security_windows
from .model import CollectionMetadata, HostSpec
from .utils.platform import platform_key


def collect_all(*, profile: str = "standard") -> HostSpec:
    plat = platform_key()

    spec = HostSpec(
        collection_metadata=CollectionMetadata(profile=profile, platform=plat)
    )

    # Core stdlib collectors.
    spec, r1 = collect_host_identity(spec)
    spec, r2 = collect_os(spec)
    spec, r3 = collect_cpu(spec)
    spec, r4 = collect_memory(spec)
    spec, r5 = collect_storage(spec)
    spec, r6 = collect_network(spec)
    spec, r7 = collect_software(spec)
    spec, r8 = collect_virtualization(spec)

    # Profile controls breadth; `minimal` skips performance snapshot.
    results = [r1, r2, r3, r4, r5, r6, r7, r8]

    if profile in {"standard", "full"}:
        spec, r9 = collect_performance_snapshot(spec)
        results.append(r9)

    # Platform-specific enrichment (stdlib-first best effort).
    if plat == "windows":
        spec, rf = collect_firmware_windows(spec)
        spec, rs = collect_security_windows(spec)
        results.extend([rf, rs])

    # Attach collector results deterministically in run order.
    meta = replace(spec.collection_metadata, results=tuple(results))
    return replace(spec, collection_metadata=meta)
