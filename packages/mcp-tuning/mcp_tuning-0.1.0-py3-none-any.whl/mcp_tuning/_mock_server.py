from __future__ import annotations

import json
import sys
from typing import Any


def _read_message(stream) -> dict[str, Any]:
    line = stream.readline()
    if not line:
        raise EOFError
    try:
        obj = json.loads(line)
    except Exception as e:
        raise ValueError(f"Invalid JSON line: {line!r}") from e
    if not isinstance(obj, dict):
        raise ValueError("Expected JSON object")
    return obj


def _reply(stream, req_id: Any, result: Any = None, error: dict[str, Any] | None = None) -> None:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id}
    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result
    stream.write(json.dumps(payload, ensure_ascii=False) + "\n")
    stream.flush()


def handle(req: dict[str, Any]) -> tuple[Any, Any | None, dict[str, Any] | None]:
    method = req.get("method")
    params = req.get("params") or {}

    if method == "initialize":
        return (
            req.get("id"),
            {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "mcp-tuning-mock", "version": "0.1.0"},
                "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
            },
            None,
        )

    if method == "tools/list":
        return (
            req.get("id"),
            {
                "tools": [
                    {
                        "name": "echo",
                        "description": "Echo back the provided arguments.",
                        "inputSchema": {"type": "object"},
                    },
                    {
                        "name": "add",
                        "description": "Add two numbers: {\"a\": 1, \"b\": 2}.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                            "required": ["a", "b"],
                        },
                    },
                ]
            },
            None,
        )

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if name == "echo":
            return (req.get("id"), {"echo": arguments}, None)
        if name == "add":
            try:
                a = float(arguments.get("a"))
                b = float(arguments.get("b"))
            except Exception:
                return (req.get("id"), None, {"code": -32602, "message": "Invalid params for add"})
            return (req.get("id"), {"sum": a + b}, None)
        return (req.get("id"), None, {"code": -32601, "message": f"Unknown tool: {name}"})

    if method == "resources/list":
        return (
            req.get("id"),
            {
                "resources": [
                    {
                        "uri": "mock://hello.txt",
                        "name": "hello",
                        "description": "A simple mock text resource.",
                        "mimeType": "text/plain",
                    }
                ]
            },
            None,
        )

    if method == "resources/read":
        uri = params.get("uri")
        if uri != "mock://hello.txt":
            return (req.get("id"), None, {"code": -32602, "message": "Unknown resource uri"})
        return (req.get("id"), {"contents": [{"uri": uri, "text": "hello from mock server"}]}, None)

    if method == "prompts/list":
        return (
            req.get("id"),
            {"prompts": [{"name": "hello", "description": "A mock prompt."}]},
            None,
        )

    if method == "prompts/get":
        name = params.get("name")
        if name != "hello":
            return (req.get("id"), None, {"code": -32602, "message": "Unknown prompt"})
        return (
            req.get("id"),
            {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": "hello from mock prompt"}],
                    }
                ]
            },
            None,
        )

    if method == "initialized":
        return (None, None, None)

    return (req.get("id"), None, {"code": -32601, "message": f"Method not found: {method}"})


def main() -> int:
    inp = sys.stdin
    out = sys.stdout
    while True:
        try:
            req = _read_message(inp)
        except EOFError:
            return 0
        except Exception as e:
            sys.stderr.write(f"mock_server: read error: {e}\n")
            sys.stderr.flush()
            return 1

        req_id, result, error = handle(req)
        if req_id is None:
            continue
        _reply(out, req_id, result=result, error=error)


if __name__ == "__main__":
    raise SystemExit(main())
