from __future__ import annotations

import json
import subprocess
import threading
import time
from collections import deque
from queue import Empty, Queue
from typing import Any

from ..models import LogEvent, utc_now_iso
from ._base import Transport


class StdioTransport(Transport):
    """
    JSON-RPC over stdio using **JSON-lines** framing (one JSON object per line).

    This transport is compatible with `mcp.server.fastmcp.FastMCP` stdio servers,
    and avoids the Windows tempfile limitations that affect asyncio's subprocess pipes
    in some restricted environments.
    """

    def __init__(
        self,
        command: list[str] | str,
        *,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        self._command = command
        self._cwd = cwd
        self._env = env

        self._process: subprocess.Popen[str] | None = None
        self._reader: threading.Thread | None = None
        self._stderr_reader: threading.Thread | None = None
        self._stop = threading.Event()

        self._next_id = 1
        self._pending_lock = threading.Lock()
        self._pending: dict[int, "Queue[dict[str, Any]]"] = {}

        self._stderr_lines: "deque[str]" = deque(maxlen=400)
        self._events: "deque[LogEvent]" = deque(maxlen=1000)
        self._server_info: dict[str, Any] | None = None

    def _emit(self, direction: str, message: dict[str, Any], meta: dict[str, Any] | None = None) -> None:
        self._events.append(LogEvent(ts=utc_now_iso(), direction=direction, message=message, meta=meta or {}))

    def start(self) -> None:
        if self._process is not None:
            return

        if isinstance(self._command, str):
            popen_args = {"args": self._command, "shell": True}
        else:
            popen_args = {"args": self._command, "shell": False}

        self._process = subprocess.Popen(
            **popen_args,
            cwd=self._cwd,
            env=self._env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        if self._process.stdin is None or self._process.stdout is None or self._process.stderr is None:
            raise RuntimeError("Failed to open stdio pipes")

        self._stop.clear()
        self._reader = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader.start()
        self._stderr_reader = threading.Thread(target=self._stderr_loop, daemon=True)
        self._stderr_reader.start()

    def close(self) -> None:
        self._stop.set()
        proc = self._process
        self._process = None
        if proc is None:
            return
        try:
            if proc.stdin:
                proc.stdin.close()
        finally:
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def _stderr_loop(self) -> None:
        assert self._process is not None and self._process.stderr is not None
        for line in self._process.stderr:
            if self._stop.is_set():
                return
            s = line.rstrip("\r\n")
            if s:
                self._stderr_lines.append(s)

    def _reader_loop(self) -> None:
        assert self._process is not None and self._process.stdout is not None
        for line in self._process.stdout:
            if self._stop.is_set():
                return
            s = line.strip()
            if not s:
                continue
            try:
                msg = json.loads(s)
            except Exception:
                # Ignore non-JSON output on stdout; treat as noise.
                continue

            if not isinstance(msg, dict):
                continue
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

    def stderr_tail(self, n: int = 200) -> list[str]:
        if n <= 0:
            return []
        return list(self._stderr_lines)[-n:]

    def events_tail(self, n: int = 200) -> list[LogEvent]:
        if n <= 0:
            return []
        return list(self._events)[-n:]

    def server_info(self) -> dict[str, Any] | None:
        return self._server_info

    def _send(self, payload: dict[str, Any]) -> None:
        if self._process is None or self._process.stdin is None:
            raise RuntimeError("Transport not started")
        self._emit("send", payload)
        self._process.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self._process.stdin.flush()

    def request(self, method: str, params: dict[str, Any] | None = None, *, timeout_s: float = 30) -> Any:
        request_id = self._next_id
        self._next_id += 1

        q: "Queue[dict[str, Any]]" = Queue(maxsize=1)
        with self._pending_lock:
            self._pending[request_id] = q

        payload: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            payload["params"] = params

        start = time.monotonic()
        try:
            self._send(payload)
            try:
                msg = q.get(timeout=timeout_s)
            except Empty as e:
                stderr = self.stderr_tail(50)
                if stderr:
                    raise TimeoutError(
                        f"Timeout waiting for response to {method}.\n--- server stderr (tail) ---\n" + "\n".join(stderr)
                    ) from e
                raise TimeoutError(f"Timeout waiting for response to {method}") from e

            if msg.get("error"):
                raise RuntimeError(str(msg["error"]))
            result = msg.get("result")
            if method == "initialize" and isinstance(result, dict):
                self._server_info = result
            return result
        finally:
            with self._pending_lock:
                self._pending.pop(request_id, None)
            duration_ms = round((time.monotonic() - start) * 1000.0, 2)
            self._emit("recv", {"id": request_id, "method": method}, meta={"duration_ms": duration_ms})

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        self._send(payload)
