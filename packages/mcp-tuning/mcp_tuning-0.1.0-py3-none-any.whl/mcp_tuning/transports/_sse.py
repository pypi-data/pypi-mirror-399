from __future__ import annotations

import json
import threading
import time
from collections import deque
from queue import Empty, Queue
from typing import Any
from urllib.request import Request, urlopen

from ..models import LogEvent, utc_now_iso
from ._base import Transport


class SseTransport(Transport):
    def __init__(
        self,
        *,
        sse_url: str,
        rpc_url: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._sse_url = sse_url
        self._rpc_url = rpc_url
        self._headers = dict(headers or {})

        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

        self._events: "deque[LogEvent]" = deque(maxlen=1000)
        self._next_id = 1
        self._pending_lock = threading.Lock()
        self._pending: dict[int, "Queue[dict[str, Any]]"] = {}
        self._server_info: dict[str, Any] | None = None

    def start(self) -> None:
        if self._thread is not None:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._sse_loop, daemon=True)
        self._thread.start()

    def close(self) -> None:
        self._stop.set()

    def is_running(self) -> bool:
        return not self._stop.is_set()

    def _emit(self, direction: str, message: dict[str, Any], meta: dict[str, Any] | None = None) -> None:
        self._events.append(LogEvent(ts=utc_now_iso(), direction=direction, message=message, meta=meta or {}))

    def _open_sse(self):
        req = Request(self._sse_url, method="GET")
        req.add_header("Accept", "text/event-stream")
        for k, v in self._headers.items():
            req.add_header(k, v)
        return urlopen(req, timeout=30)

    def _sse_loop(self) -> None:
        try:
            with self._open_sse() as resp:
                buf: list[str] = []
                while not self._stop.is_set():
                    line = resp.readline()
                    if not line:
                        return
                    text = line.decode("utf-8", errors="replace").rstrip("\r\n")
                    if text == "":
                        if not buf:
                            continue
                        data = "\n".join(buf)
                        buf.clear()
                        try:
                            msg = json.loads(data)
                        except Exception:
                            continue
                        if isinstance(msg, dict):
                            self._emit("recv", msg)
                            msg_id = msg.get("id")
                            if msg_id is None:
                                continue
                            try:
                                msg_id_int = int(msg_id)
                            except Exception:
                                continue
                            with self._pending_lock:
                                q = self._pending.get(msg_id_int)
                            if q is not None:
                                q.put(msg)
                        continue

                    if text.startswith(":"):
                        continue
                    if text.startswith("data:"):
                        buf.append(text[len("data:") :].lstrip())
        except Exception:
            return

    def _post(self, payload: dict[str, Any], *, timeout_s: float) -> dict[str, Any] | None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = Request(self._rpc_url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        for k, v in self._headers.items():
            req.add_header(k, v)
        with urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read()
        if not raw:
            return None
        obj = json.loads(raw.decode("utf-8"))
        return obj if isinstance(obj, dict) else None

    def request(self, method: str, params: dict[str, Any] | None = None, *, timeout_s: float = 30) -> Any:
        req_id = self._next_id
        self._next_id += 1
        payload: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params is not None:
            payload["params"] = params

        q: "Queue[dict[str, Any]]" = Queue(maxsize=1)
        with self._pending_lock:
            self._pending[req_id] = q

        start = time.monotonic()
        self._emit("send", payload)
        direct = self._post(payload, timeout_s=min(timeout_s, 30))
        if direct is not None:
            self._emit("recv", direct, meta={"duration_ms": round((time.monotonic() - start) * 1000.0, 2)})
            with self._pending_lock:
                self._pending.pop(req_id, None)
            if direct.get("error"):
                raise RuntimeError(str(direct["error"]))
            result = direct.get("result")
            if method == "initialize" and isinstance(result, dict):
                self._server_info = result
            return result

        try:
            msg = q.get(timeout=timeout_s)
        except Empty as e:
            raise TimeoutError(f"Timeout waiting for SSE response to {method}") from e
        finally:
            with self._pending_lock:
                self._pending.pop(req_id, None)

        duration_ms = round((time.monotonic() - start) * 1000.0, 2)
        self._emit("recv", msg, meta={"duration_ms": duration_ms})
        if msg.get("error"):
            raise RuntimeError(str(msg["error"]))
        result = msg.get("result")
        if method == "initialize" and isinstance(result, dict):
            self._server_info = result
        return result

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        self._emit("send", payload)
        _ = self._post(payload, timeout_s=5)

    def stderr_tail(self, n: int = 200) -> list[str]:
        return []

    def events_tail(self, n: int = 200) -> list[LogEvent]:
        if n <= 0:
            return []
        items = list(self._events)
        return items[-n:]

    def server_info(self) -> dict[str, Any] | None:
        return self._server_info
