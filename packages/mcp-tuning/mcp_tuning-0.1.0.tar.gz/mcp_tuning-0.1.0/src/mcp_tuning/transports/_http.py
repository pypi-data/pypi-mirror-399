from __future__ import annotations

import json
import time
from collections import deque
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..models import LogEvent, utc_now_iso
from ._base import Transport


class HttpTransport(Transport):
    def __init__(self, rpc_url: str, *, headers: dict[str, str] | None = None) -> None:
        self._rpc_url = rpc_url
        self._headers = dict(headers or {})
        self._events: "deque[LogEvent]" = deque(maxlen=500)
        self._next_id = 1
        self._server_info: dict[str, Any] | None = None

    def start(self) -> None:
        return

    def close(self) -> None:
        return

    def is_running(self) -> bool:
        return True

    def _emit(self, direction: str, message: dict[str, Any], meta: dict[str, Any] | None = None) -> None:
        self._events.append(LogEvent(ts=utc_now_iso(), direction=direction, message=message, meta=meta or {}))

    def _post_json(self, payload: dict[str, Any], *, timeout_s: float) -> dict[str, Any] | None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = Request(self._rpc_url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        for k, v in self._headers.items():
            req.add_header(k, v)

        start = time.monotonic()
        try:
            with urlopen(req, timeout=timeout_s) as resp:
                raw = resp.read()
        except HTTPError as e:
            raw = e.read()
            raise RuntimeError(f"HTTP {e.code}: {raw[:200]!r}") from e
        except URLError as e:
            raise RuntimeError(f"HTTP request failed: {e}") from e

        duration_ms = round((time.monotonic() - start) * 1000.0, 2)
        if not raw:
            return None
        try:
            obj = json.loads(raw.decode("utf-8"))
        except Exception as e:
            raise RuntimeError(f"Invalid JSON response: {raw[:200]!r}") from e
        if isinstance(obj, dict):
            obj_meta = {"duration_ms": duration_ms}
            self._emit("recv", obj, meta=obj_meta)
            return obj
        return None

    def request(self, method: str, params: dict[str, Any] | None = None, *, timeout_s: float = 30) -> Any:
        req_id = self._next_id
        self._next_id += 1
        payload: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params is not None:
            payload["params"] = params
        self._emit("send", payload)

        resp = self._post_json(payload, timeout_s=timeout_s)
        if resp is None:
            raise TimeoutError(f"No response for {method}")
        if resp.get("error"):
            raise RuntimeError(str(resp["error"]))
        result = resp.get("result")
        if method == "initialize" and isinstance(result, dict):
            self._server_info = result
        return result

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        self._emit("send", payload)
        _ = self._post_json(payload, timeout_s=5)

    def stderr_tail(self, n: int = 200) -> list[str]:
        return []

    def events_tail(self, n: int = 200) -> list[LogEvent]:
        if n <= 0:
            return []
        items = list(self._events)
        return items[-n:]

    def server_info(self) -> dict[str, Any] | None:
        return self._server_info
