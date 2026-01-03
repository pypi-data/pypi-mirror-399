from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from mcp.server.fastmcp import FastMCP


server = FastMCP("simple-stdio-server")


@server.tool(description="Echo a message back.")
def echo(message: str) -> dict[str, Any]:
    return {"echo": message}


@server.tool(description="Echo a JSON object back.")
def echo_json(payload: dict[str, Any]) -> dict[str, Any]:
    return {"echo": payload}


@server.tool(description="Add two numbers.")
def add(a: float, b: float) -> dict[str, Any]:
    return {"sum": a + b}


@server.tool(description="Return current UTC timestamp.")
def now_utc() -> dict[str, Any]:
    return {"ts": datetime.now(timezone.utc).isoformat()}


@server.resource(
    "simple://readme",
    name="readme",
    description="A tiny example resource.",
    mime_type="text/plain",
)
def readme() -> str:
    return "hello from examples/servers/simple_stdio_server.py"


@server.prompt(description="A tiny example prompt.")
def hello(name: str = "world") -> list[dict[str, Any]]:
    return [
        {
            "role": "user",
            "content": [{"type": "text", "text": f"hello, {name} (from examples)"}],
        }
    ]


if __name__ == "__main__":
    server.run("stdio")
