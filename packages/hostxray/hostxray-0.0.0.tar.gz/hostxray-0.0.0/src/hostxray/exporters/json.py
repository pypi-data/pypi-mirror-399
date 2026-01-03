from __future__ import annotations

from ..model import HostSpec


def to_json(spec: HostSpec, *, indent: int | None = None) -> str:
    return spec.to_json(indent=indent)
