from __future__ import annotations

from hostxray.model import HostIdentity, HostSpec, NetworkInfo, NetworkInterface
from hostxray.redaction import RedactionCategory, RedactionConfig


def test_redaction_masks_hostname_and_network():
    spec = HostSpec(
        host_identity=HostIdentity(hostname="MYHOST", fqdn="MYHOST.example.com", machine_id="abc"),
        network=NetworkInfo(
            interfaces=(
                NetworkInterface(name="eth0", mac="aa:bb:cc:dd:ee:ff", ipv4=("10.0.0.1",), ipv6=("::1",)),
            ),
            dns_servers=("8.8.8.8",),
            gateways=("10.0.0.254",),
        ),
        redaction=RedactionConfig(
            enabled=True,
            categories={
                RedactionCategory.hostname,
                RedactionCategory.serial,
                RedactionCategory.mac,
                RedactionCategory.ip,
            },
        ),
    )

    red = spec.redacted()
    assert red.host_identity.hostname == "[REDACTED]"
    assert red.host_identity.fqdn == "[REDACTED]"
    assert red.host_identity.machine_id == "[REDACTED]"
    assert red.network.interfaces[0].mac == "[REDACTED]"
    assert red.network.interfaces[0].ipv4 == ()
    assert red.network.interfaces[0].ipv6 == ()
    assert red.network.dns_servers == ()
    assert red.network.gateways == ()
