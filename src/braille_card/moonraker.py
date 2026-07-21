"""Small, explicit Moonraker client used by the local operator workspace."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class MoonrakerError(RuntimeError):
    """A remote-status request could not be completed safely."""


@dataclass(frozen=True)
class MoonrakerClient:
    """Moonraker client with an intentionally read-only status surface.

    This class does not expose G-code, restart, upload, or print-start methods.
    Keeping this narrow makes a browser status refresh incapable of changing a
    printer's state.
    """

    base_url: str
    api_key: str | None = None
    bearer_token: str | None = None
    timeout_seconds: float = 5.0

    def __post_init__(self) -> None:
        parsed = urlparse(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("MOONRAKER_URL must be a complete http(s) URL")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("MOONRAKER_URL must not contain credentials, a query, or a fragment")
        if self.api_key and self.bearer_token:
            raise ValueError("Configure either a Moonraker API key or bearer token, not both")

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.api_key:
            headers["X-Api-Key"] = self.api_key
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        return headers

    def read_status(self) -> dict[str, Any]:
        """Return selected printer status through Moonraker's query endpoint."""
        body = {
            "objects": {
                "webhooks": ["state", "state_message"],
                "print_stats": ["filename", "state", "message", "print_duration"],
                "virtual_sdcard": ["file_path", "progress", "is_active"],
                "extruder": ["temperature", "target"],
                "heater_bed": ["temperature", "target"],
            }
        }
        payload = json.dumps(body, separators=(",", ":")).encode("utf-8")
        request = Request(
            self.base_url.rstrip("/") + "/printer/objects/query",
            data=payload,
            headers=self._headers(),
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:  # noqa: S310 - operator-configured endpoint
                decoded = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            raise MoonrakerError("Moonraker status request failed") from exc
        if not isinstance(decoded, dict):
            raise MoonrakerError("Moonraker returned an invalid status response")
        result = decoded.get("result", decoded)
        if not isinstance(result, dict) or not isinstance(result.get("status"), dict):
            raise MoonrakerError("Moonraker status response did not contain printer objects")
        return result["status"]
