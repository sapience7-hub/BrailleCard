from __future__ import annotations

import json
from email.message import Message

import pytest

from braille_card.moonraker import MoonrakerClient


class _Response:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.headers = Message()

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args) -> None:
        return None


def test_read_status_uses_only_moonraker_query_endpoint(monkeypatch) -> None:
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["method"] = request.get_method()
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data)
        return _Response({"result": {"status": {"webhooks": {"state": "ready"}}}})

    monkeypatch.setattr("braille_card.moonraker.urlopen", fake_urlopen)
    status = MoonrakerClient("http://printer.local/api", api_key="secret").read_status()

    assert status == {"webhooks": {"state": "ready"}}
    assert captured["url"] == "http://printer.local/api/printer/objects/query"
    assert captured["method"] == "POST"
    assert captured["headers"]["X-api-key"] == "secret"
    assert set(captured["body"]["objects"]) == {
        "webhooks", "print_stats", "virtual_sdcard", "extruder", "heater_bed"
    }


@pytest.mark.parametrize("url", ["printer.local", "file:///tmp/printer", "http://user:pass@printer.local"])
def test_client_rejects_unsafe_or_incomplete_urls(url: str) -> None:
    with pytest.raises(ValueError):
        MoonrakerClient(url)


def test_client_rejects_two_authentication_schemes() -> None:
    with pytest.raises(ValueError, match="either"):
        MoonrakerClient("http://printer.local", api_key="key", bearer_token="token")
