from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import HostSpec


class RedactionCategory(str, Enum):
    hostname = "hostname"
    user = "user"
    serial = "serial"
    mac = "mac"
    ip = "ip"


@dataclass(frozen=True, slots=True)
class RedactionConfig:
    enabled: bool = False
    categories: set[RedactionCategory] = field(default_factory=set)


DEFAULT_SAFE_MODE: set[RedactionCategory] = {
    RedactionCategory.hostname,
    RedactionCategory.user,
    RedactionCategory.serial,
    RedactionCategory.mac,
    RedactionCategory.ip,
}


def normalize_redaction_config(
    *, safe_mode: bool, redaction: RedactionConfig | None
) -> RedactionConfig:
    if redaction is not None:
        return redaction

    if safe_mode:
        return RedactionConfig(enabled=True, categories=set(DEFAULT_SAFE_MODE))

    return RedactionConfig(enabled=False, categories=set())


def _mask(value: str | None) -> str | None:
    if value is None:
        return None
    return "[REDACTED]"


def apply_redaction(spec: "HostSpec", cfg: RedactionConfig) -> "HostSpec":
    if not cfg.enabled:
        return spec

    host = spec.host_identity
    net = spec.network

    if RedactionCategory.hostname in cfg.categories:
        host = replace(host, hostname=_mask(host.hostname), fqdn=_mask(host.fqdn))

    if RedactionCategory.serial in cfg.categories:
        host = replace(host, machine_id=_mask(host.machine_id))

    if RedactionCategory.ip in cfg.categories:
        interfaces = []
        for iface in net.interfaces:
            interfaces.append(replace(iface, ipv4=(), ipv6=()))
        net = replace(net, interfaces=tuple(interfaces), dns_servers=(), gateways=())

    if RedactionCategory.mac in cfg.categories:
        interfaces = []
        for iface in net.interfaces:
            interfaces.append(replace(iface, mac=_mask(iface.mac)))
        net = replace(net, interfaces=tuple(interfaces))

    # "user" is currently enforced via collectors (avoid collecting usernames);
    # kept as a category for forward compatibility.

    return replace(spec, host_identity=host, network=net, redaction=cfg)
