from __future__ import annotations

import json

from hostxray.model import HostSpec


def test_spec_is_json_serializable():
    spec = HostSpec()
    payload = spec.to_json()
    obj = json.loads(payload)
    assert "host_identity" in obj
    assert "collection_metadata" in obj
