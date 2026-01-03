from __future__ import annotations

import json
import subprocess
import threading
import time
from collections import deque
from dataclasses import dataclass
from queue import Empty, Queue
from typing import Any, Callable, Dict, List, Optional, Union

from .models import LogEvent, utc_now_iso


class MCPProtocolError(RuntimeError):
    pass


@dataclass(frozen=True)
class JsonRpcError:
    code: int
    message: str
    data: Any | None = None


def _encode_lsp_message(payload: Dict[str, Any]) -> bytes:
    """將字典編碼為帶有 Content-Length 頭的 LSP 格式字節流。"""
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    return header + body


def _read_exact(stream, n: int) -> bytes:
    """從流中讀取確切的 n 個字節。"""
    data = stream.read(n)
    if len(data) < n:
        raise EOFError(f"Expected {n} bytes, got {len(data)}")
    return data


def _read_lsp_message(stream) -> Dict[str, Any]:
    """
    從流中讀取並解析 LSP 消息。
    優化：使用 readline() 代替逐字節讀取以提高 Header 解析效率。
    """
    content_length = -1

    while True:
        # 使用 readline 讀取標頭行，這比 read(1) 快得多
        line = stream.readline()
        if not line:
            raise EOFError("Unexpected EOF while reading headers")

        line = line.strip()
        if not line:
            # 空行表示 Header 結束
            break

        # 解析 Content-Length
        # 這裡做了一個優化：只檢查我們關心的 Header，忽略其他的
        if line.lower().startswith(b"content-length:"):
            try:
                _, value = line.split(b":", 1)
                content_length = int(value.strip())
            except ValueError as e:
                raise MCPProtocolError("Invalid Content-Length header") from e

    if content_length < 0:
        raise MCPProtocolError("Missing Content-Length header")

    body = _read_exact(stream, content_length)
    try:
        return json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise MCPProtocolError("Invalid JSON payload") from e


class MCPStdioClient:
    def __init__(
        self,
        command: Union[List[str], str],
        *,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        on_event: Optional[Callable[[LogEvent], None]] = None,
    ) -> None:
        self._command = command
        self._cwd = cwd
        self._env = env
        self._on_event = on_event

        self._process: Optional[subprocess.Popen[bytes]] = None
        self._reader_thread: Optional[threading.Thread] = None
        self._stderr_thread: Optional[threading.Thread] = None
        self._stop = threading.Event()

        self._next_id = 1
        # 使用線程安全的 Queue 和 deque
        self._notifications: Queue[Dict[str, Any]] = Queue()
        self._stderr_lines: deque[str] = deque(maxlen=200)
        self._events: deque[LogEvent] = deque(maxlen=500)

        # 請求管理
        self._pending_lock = threading.Lock()
        self._pending: Dict[int, Queue[Dict[str, Any]]] = {}
        self._orphan_responses: Dict[int, Dict[str, Any]] = {}
        self._request_start: Dict[int, float] = {}

        self._server_info: Optional[Dict[str, Any]] = None

    def start(self) -> None:
        if self._process is not None:
            return

        popen_kwargs = {
            "cwd": self._cwd,
            "env": self._env,
            "stdin": subprocess.PIPE,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "bufsize": 0,  # 禁用緩衝以減少延遲
        }

        if isinstance(self._command, str):
            self._process = subprocess.Popen(self._command, shell=True, **popen_kwargs)
        else:
            self._process = subprocess.Popen(self._command, shell=False, **popen_kwargs)

        if self._process.stdin is None or self._process.stdout is None:
            raise RuntimeError("Failed to open stdio pipes")

        self._stop.clear()

        # 啟動線程
        self._reader_thread = threading.Thread(
            target=self._reader_loop, name="MCP-Reader", daemon=True
        )
        self._stderr_thread = threading.Thread(
            target=self._stderr_loop, name="MCP-Stderr", daemon=True
        )

        self._reader_thread.start()
        self._stderr_thread.start()

    def close(self) -> None:
        if self._stop.is_set():
            return

        self._stop.set()
        proc = self._process
        self._process = None

        if proc is None:
            return

        # 關閉 stdin 會觸發子進程的 EOF，有助於它自行退出
        try:
            if proc.stdin:
                proc.stdin.close()
        except (BrokenPipeError, OSError):
            pass

        # 優雅終止流程
        try:
            proc.terminate()
            proc.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=1.0)
        except Exception:
            # 如果進程已經消失，忽略錯誤
            pass

    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def exit_code(self) -> Optional[int]:
        if self._process is None:
            return None
        return self._process.poll()

    def __enter__(self) -> MCPStdioClient:
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _emit_event(
        self,
        direction: str,
        message: Dict[str, Any],
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        # 快速檢查是否有監聽者，避免不必要的物件創建
        if self._on_event is None and len(self._events) == self._events.maxlen:
            # 如果沒有外部監聽且內部 deque 滿了，這裡可以做一些優化，但為了保持邏輯簡單，繼續執行
            pass

        event = LogEvent(
            ts=utc_now_iso(), direction=direction, message=message, meta=meta or {}
        )
        self._events.append(event)

        if self._on_event:
            try:
                self._on_event(event)
            except Exception:
                # 防止用戶的回調函數崩潰影響 Client
                pass

    def _reader_loop(self) -> None:
        """讀取 stdout 並分發消息的主循環"""
        assert self._process is not None and self._process.stdout is not None
        stream = self._process.stdout

        while not self._stop.is_set():
            try:
                msg = _read_lsp_message(stream)
            except (EOFError, OSError):
                # 進程結束或管道關閉
                break
            except Exception as e:
                self._notifications.put(
                    {
                        "jsonrpc": "2.0",
                        "method": "mcp_tuning/reader_error",
                        "params": {"message": str(e)},
                    }
                )
                break

            msg_id = msg.get("id")

            # 情況 1: Notification (沒有 ID)
            if msg_id is None:
                self._emit_event("recv", msg)
                self._notifications.put(msg)
                continue

            # 情況 2: Response (有 ID)
            try:
                msg_id_int = int(msg_id)
            except (ValueError, TypeError):
                # ID 格式錯誤，視為普通消息處理
                self._emit_event("recv", msg)
                self._notifications.put(msg)
                continue

            # 計算耗時
            duration_ms: Optional[float] = None
            with self._pending_lock:
                start_time = self._request_start.pop(msg_id_int, None)

            if start_time is not None:
                duration_ms = round((time.monotonic() - start_time) * 1000.0, 2)

            self._emit_event(
                "recv",
                msg,
                meta={"duration_ms": duration_ms} if duration_ms is not None else None,
            )

            # 分發響應
            with self._pending_lock:
                q = self._pending.get(msg_id_int)
                if q:
                    q.put(msg)
                else:
                    # 如果沒有等待者（可能超時了），存入孤兒區
                    self._orphan_responses[msg_id_int] = msg

    def _stderr_loop(self) -> None:
        assert self._process is not None and self._process.stderr is not None
        stream = self._process.stderr

        while not self._stop.is_set():
            line = stream.readline()
            if not line:
                break
            try:
                text = line.decode("utf-8", errors="replace").rstrip("\r\n")
            except Exception:
                text = str(line)
            self._stderr_lines.append(text)

    # --- API Methods ---

    def stderr_tail(self, n: int = 200) -> List[str]:
        if n <= 0:
            return []
        return list(self._stderr_lines)[-n:]

    def events_tail(self, n: int = 200) -> List[LogEvent]:
        if n <= 0:
            return []
        return list(self._events)[-n:]

    def notifications_tail(self, n: int = 50) -> List[Dict[str, Any]]:
        if n <= 0:
            return []
        items = []
        # 使用 range 避免 while True，並確保不會無限阻塞
        for _ in range(n):
            try:
                items.append(self._notifications.get_nowait())
            except Empty:
                break
        return items

    def _send(self, payload: Dict[str, Any]) -> None:
        if self._process is None or self._process.stdin is None:
            raise RuntimeError("Client not started")

        # 記錄請求開始時間
        msg_id = payload.get("id")
        if msg_id is not None:
            with self._pending_lock:
                self._request_start[int(msg_id)] = time.monotonic()

        self._emit_event("send", payload)
        data = _encode_lsp_message(payload)

        try:
            self._process.stdin.write(data)
            self._process.stdin.flush()
        except BrokenPipeError:
            # 嘗試優雅處理管道斷裂
            raise RuntimeError("Server process disconnected")

    def _create_timeout_error(self, method: str, cause: Exception) -> TimeoutError:
        """輔助方法：生成包含 stderr 詳細信息的超時錯誤"""
        exit_code = self.exit_code()
        stderr_tail = self.stderr_tail(50)

        detail_parts = [f"Timeout waiting for response to {method}."]

        if exit_code is not None:
            detail_parts.append(f"Process exited with code {exit_code}.")

        if stderr_tail:
            detail_parts.append("--- server stderr (tail) ---")
            detail_parts.extend(stderr_tail)

        return TimeoutError("\n".join(detail_parts))

    def request(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        *,
        timeout_s: float = 30,
    ) -> Any:
        request_id = self._next_id
        self._next_id += 1

        payload = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            payload["params"] = params

        # 創建單次使用的 Queue 來接收結果
        q: Queue[Dict[str, Any]] = Queue(maxsize=1)

        with self._pending_lock:
            self._pending[request_id] = q
            # 檢查是否已經有孤兒響應（極少見情況，但為了健壯性）
            orphan = self._orphan_responses.pop(request_id, None)
            if orphan:
                q.put(orphan)

        try:
            self._send(payload)
            msg = q.get(timeout=timeout_s)
        except Empty as e:
            raise self._create_timeout_error(method, e) from e
        finally:
            # 清理 pending 狀態
            with self._pending_lock:
                self._pending.pop(request_id, None)
                self._request_start.pop(request_id, None)

        # 檢查 JSON-RPC 錯誤
        if "error" in msg:
            err = msg["error"]
            if err:
                raise MCPProtocolError(
                    JsonRpcError(
                        code=int(err.get("code", -32000)),
                        message=str(err.get("message", "Unknown error")),
                        data=err.get("data"),
                    )
                )

        return msg.get("result")

    def notify(self, method: str, params: Optional[Dict[str, Any]] = None) -> None:
        payload = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        self._send(payload)

    # --- MCP Specific Methods (Wrappers) ---

    def initialize(
        self,
        *,
        protocol_version: str = "2024-11-05",
        client_name: str = "mcp-tuning",
        client_version: str = "0.1.0",
        capabilities: Optional[Dict[str, Any]] = None,
        timeout_s: float = 30,
    ) -> Any:
        params = {
            "protocolVersion": protocol_version,
            "clientInfo": {"name": client_name, "version": client_version},
            "capabilities": capabilities or {},
        }
        result = self.request("initialize", params, timeout_s=timeout_s)
        if isinstance(result, dict):
            self._server_info = result
        return result

    def server_info(self) -> Optional[Dict[str, Any]]:
        return self._server_info

    def initialized(self) -> None:
        self.notify("initialized")

    def list_tools(self, *, timeout_s: float = 30) -> Any:
        return self.request("tools/list", {}, timeout_s=timeout_s)

    def call_tool(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
        *,
        timeout_s: float = 60,
    ) -> Any:
        return self.request(
            "tools/call",
            {"name": name, "arguments": arguments or {}},
            timeout_s=timeout_s,
        )

    def list_resources(self, *, timeout_s: float = 30) -> Any:
        return self.request("resources/list", {}, timeout_s=timeout_s)

    def read_resource(self, uri: str, *, timeout_s: float = 60) -> Any:
        return self.request("resources/read", {"uri": uri}, timeout_s=timeout_s)

    def list_prompts(self, *, timeout_s: float = 30) -> Any:
        return self.request("prompts/list", {}, timeout_s=timeout_s)

    def get_prompt(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
        *,
        timeout_s: float = 60,
    ) -> Any:
        return self.request(
            "prompts/get",
            {"name": name, "arguments": arguments or {}},
            timeout_s=timeout_s,
        )
