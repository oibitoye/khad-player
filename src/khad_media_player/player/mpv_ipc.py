"""JSON IPC client for a local mpv input-ipc-server socket."""

from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Any


class MpvIpcClient:
    """Send mpv JSON IPC commands and correlate a single-line response."""

    def __init__(self, socket_path: Path, timeout: float = 1.0) -> None:
        self.socket_path = Path(socket_path)
        self.timeout = timeout
        self._request_id = 0

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def command(self, *args: Any) -> dict[str, Any]:
        """Send a command; returns parsed JSON or an error dict."""
        request_id = self._next_id()
        payload = {
            "command": list(args),
            "request_id": request_id,
        }
        try:
            with socket.socket(socket.AF_UNIX) as sock:
                sock.settimeout(self.timeout)
                sock.connect(str(self.socket_path))
                sock.sendall((json.dumps(payload) + "\n").encode())
                data = b""
                while b"\n" not in data:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                for line in data.split(b"\n"):
                    if not line.strip():
                        continue
                    message = json.loads(line)
                    # Prefer the correlated response; fall back to first object
                    # for older mpv builds that omit request_id.
                    if message.get("request_id") in (None, request_id):
                        if "event" in message and "error" not in message:
                            continue
                        return message
                return {"error": "Player not ready"}
        except (OSError, ValueError, IndexError, json.JSONDecodeError):
            return {"error": "Player not ready"}

    def is_ready(self) -> bool:
        result = self.command("get_property", "mpv-version")
        return result.get("error") == "success"
