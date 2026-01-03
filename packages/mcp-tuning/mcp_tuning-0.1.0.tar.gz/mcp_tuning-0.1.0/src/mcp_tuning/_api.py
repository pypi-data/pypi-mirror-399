from __future__ import annotations

import shlex
from pathlib import Path
from typing import Any

from ._inspector import InspectorClient
from .client import Client


def _find_project_root(start: Path | None = None) -> Path:
    p = (start or Path.cwd()).resolve()
    for cur in [p, *p.parents]:
        if (cur / "pyproject.toml").exists():
            return cur
    return p


def _venv_python(project_root: Path) -> Path | None:
    candidates = [
        project_root / ".venv" / "Scripts" / "python.exe",
        project_root / ".venv" / "bin" / "python",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _normalize_stdio_command(command: list[str] | str, project_root: Path) -> list[str] | str:
    if isinstance(command, str):
        text = command.strip()
        try:
            argv = shlex.split(text, posix=False)
        except ValueError:
            return text
        command = argv

    if not command:
        raise ValueError("Empty command")

    if len(command) >= 3 and str(command[0]).lower() == "uv" and str(command[1]).lower() == "run":
        py = str(command[2]).lower()
        if py in ("python", "python.exe"):
            venv_py = _venv_python(project_root)
            if venv_py is not None:
                return [str(venv_py), *[str(x) for x in command[3:]]]
    return command


def connect_stdio(
    command: list[str] | str,
    *,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
) -> Client:
    """
    Connect to an MCP server over stdio (subprocess).

    - `command` can be `list[str]` (recommended) or a shell string.
    - Runs from the project root by default so relative paths behave consistently in notebooks.
    """
    inspector = InspectorClient()
    project_root = _find_project_root()
    command = _normalize_stdio_command(command, project_root)
    inspector.connect_stdio(command, cwd=cwd or str(project_root), env=env)
    return Client(inspector)


def connect_http(rpc_url: str, *, headers: dict[str, str] | None = None) -> Client:
    """Connect to an MCP server over HTTP JSON-RPC (POST)."""
    inspector = InspectorClient()
    inspector.connect_http(rpc_url, headers=headers)
    return Client(inspector)


def connect_sse(*, sse_url: str, rpc_url: str, headers: dict[str, str] | None = None) -> Client:
    """Connect to an MCP server using SSE (stream) + HTTP (POST)."""
    inspector = InspectorClient()
    inspector.connect_sse(sse_url=sse_url, rpc_url=rpc_url, headers=headers)
    return Client(inspector)

