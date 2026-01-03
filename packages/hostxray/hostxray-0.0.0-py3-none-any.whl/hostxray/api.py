from __future__ import annotations

from dataclasses import replace

from .collect import collect_all
from .model import HostSpec
from .redaction import RedactionConfig, normalize_redaction_config


def collect_spec(
    *,
    profile: str = "standard",
    safe_mode: bool = True,
    redaction: RedactionConfig | None = None,
) -> HostSpec:
    """Collect a best-effort host specification.

    - Never raises due to missing fields (best-effort)
    - Deterministic ordering and JSON-ready
    - Safe mode redacts sensitive identifiers by default

    Args:
        profile: "minimal" | "standard" | "full"
        safe_mode: If True, apply default redactions.
        redaction: Explicit redaction config. If provided, overrides safe_mode.

    Returns:
        HostSpec
    """

    spec = collect_all(profile=profile)

    cfg = normalize_redaction_config(safe_mode=safe_mode, redaction=redaction)
    if cfg.enabled:
        return replace(spec, redaction=cfg).redacted()

    return replace(spec, redaction=cfg)
