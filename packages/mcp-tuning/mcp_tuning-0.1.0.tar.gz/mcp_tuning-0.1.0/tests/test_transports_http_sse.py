import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from queue import Queue
from typing import Any
from urllib.parse import urlparse

from mcp_tuning.transports._http import HttpTransport
from mcp_tuning.transports._sse import SseTransport


def _handle_jsonrpc(req: dict[str, Any]) -> dict[str, Any] | None:
    method = req.get("method")
    params = req.get("params") or {}
    rid = req.get("id")
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "test-http", "version": "0.0.0"},
                "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": [{"name": "echo"}]}}
    if method == "tools/call":
        return {"jsonrpc": "2.0", "id": rid, "result": {"echo": params.get("arguments") or {}}}
    if method == "resources/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"resources": [{"uri": "http://example/res"}]}}
    if method == "resources/read":
        return {"jsonrpc": "2.0", "id": rid, "result": {"contents": [{"uri": params.get("uri"), "text": "hi"}]}}
    if method == "prompts/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"prompts": [{"name": "hello"}]}}
    if method == "prompts/get":
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {"messages": [{"role": "user", "content": [{"type": "text", "text": "hi"}]}]},
        }
    if rid is None:
        return None
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "Method not found"}}


class _Server:
    def __init__(self):
        self.sse_clients: list[Any] = []
        self.sse_queue: "Queue[dict[str, Any]]" = Queue()
        self.stop = threading.Event()

        server = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def _send_json(self, obj: dict[str, Any], code: int = 200):
                data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_POST(self):
                if self.path != "/rpc":
                    self.send_error(404)
                    return
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length)
                req = json.loads(raw.decode("utf-8"))
                resp = _handle_jsonrpc(req)

                # For SSE tests: if header asks async, enqueue response and return empty body.
                if self.headers.get("X-Async") == "1" and resp is not None:
                    server.sse_queue.put(resp)
                    self.send_response(202)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return

                if resp is None:
                    self.send_response(204)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                self._send_json(resp)

            def do_GET(self):
                if self.path != "/sse":
                    self.send_error(404)
                    return
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.end_headers()
                server.sse_clients.append(self.wfile)
                while not server.stop.is_set():
                    try:
                        msg = server.sse_queue.get(timeout=0.2)
                    except Exception:
                        continue
                    data = json.dumps(msg, ensure_ascii=False)
                    payload = f"data: {data}\n\n".encode("utf-8")
                    try:
                        self.wfile.write(payload)
                        self.wfile.flush()
                    except Exception:
                        return

            def log_message(self, format, *args):
                return

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)

    @property
    def base(self) -> str:
        host, port = self.httpd.server_address
        return f"http://{host}:{port}"

    def start(self):
        t = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        t.start()
        return t

    def shutdown(self):
        self.stop.set()
        self.httpd.shutdown()


def test_http_transport_roundtrip():
    srv = _Server()
    srv.start()
    t = HttpTransport(f"{srv.base}/rpc")
    t.start()
    _ = t.request("initialize", {"protocolVersion": "2024-11-05", "clientInfo": {"name": "x", "version": "y"}, "capabilities": {}})
    t.notify("initialized")
    tools = t.request("tools/list", {})
    assert tools["tools"][0]["name"] == "echo"
    res = t.request("tools/call", {"name": "echo", "arguments": {"x": 1}})
    assert res == {"echo": {"x": 1}}
    srv.shutdown()


def test_sse_transport_roundtrip():
    srv = _Server()
    srv.start()
    # Ask server to respond via SSE by marking async header.
    headers = {"X-Async": "1"}
    t = SseTransport(sse_url=f"{srv.base}/sse", rpc_url=f"{srv.base}/rpc", headers=headers)
    t.start()
    _ = t.request("initialize", {"protocolVersion": "2024-11-05", "clientInfo": {"name": "x", "version": "y"}, "capabilities": {}})
    t.notify("initialized")
    res = t.request("tools/call", {"name": "echo", "arguments": {"x": 2}}, timeout_s=5)
    assert res == {"echo": {"x": 2}}

    # Ensure we saw at least one recv event.
    ev = t.events_tail(50)
    assert any(e.direction == "recv" for e in ev)

    srv.shutdown()
