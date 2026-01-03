from __future__ import annotations

import ipaddress


def classify_ip(ip: str) -> str:
    """Return a coarse classification for troubleshooting."""
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return "invalid"

    if addr.is_loopback:
        return "loopback"
    if addr.is_link_local:
        return "link_local"
    if addr.is_private:
        return "private"
    if addr.is_global:
        return "public"
    return "other"
