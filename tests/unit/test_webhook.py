import json

import pytest

from tools.wct.webhook import deliver, payload, signature


def test_payload_has_versioned_envelope() -> None:
    body = payload("gate.completed", "sample", {"tier": "commit"})

    assert json.loads(body)["data"] == {"tier": "commit"}
    assert json.loads(body)["schema_version"] == 1


def test_signature_is_deterministic() -> None:
    assert signature(b"body", "secret") == signature(b"body", "secret")
    assert signature(b"body", "secret") != signature(b"changed", "secret")


def test_delivery_rejects_plain_http_off_localhost() -> None:
    with pytest.raises(ValueError, match="HTTPS"):
        deliver("http://example.com/hook", b"{}", secret="".join(("test", "-key")))
