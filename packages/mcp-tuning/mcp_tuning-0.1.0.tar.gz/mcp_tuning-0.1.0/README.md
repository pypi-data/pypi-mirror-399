# mcp-tuning

A **script-first** MCP debugging/testing library for Jupyter notebooks and plain Python scripts.

It is designed to help you iterate on MCP servers (implemented in any language) by providing a small, synchronous client API:

- Connect via `stdio` (subprocess), `http`, or `sse`
- Explore: tools / resources / prompts
- Call tools with JSON arguments
- Save/replay input-only cases (tool + args)
- Export logs / history / last result as JSON for repeatable debugging

Start with `examples/notebooks/01_mcp_inspector_demo.ipynb`.

## Requirements

- Python 3.12+
- `uv`

## Install (uv)

```powershell
uv sync
uv sync --extra notebook --extra test
```

## Run (Jupyter)

```powershell
uv run jupyter lab
```

## Quickstart (stdio)

Prefer argv lists for `stdio` servers (avoids shell quoting issues) and make sure the server runs in an environment that has its dependencies installed.

```python
from mcp_tuning import connect_stdio

# Example 1: connect to the built-in mock server (minimal dependencies)
import sys
c = connect_stdio([sys.executable, "src/mcp_tuning/_mock_server.py"])

print(c.server_info())
print([t.name for t in c.tools()])
print(c.call("add", {"a": 1, "b": 2}).result)
c.close()
```

Connect to the FastMCP example server (requires `mcp` installed in the interpreter that runs the server):

```python
from mcp_tuning import connect_stdio

c = connect_stdio([".venv/Scripts/python.exe", "examples/servers/simple_stdio_server.py"])
print([t.name for t in c.tools()])
print(c.call("add", {"a": 1, "b": 2}).result)
c.close()
```

## Public API Reference

The public API is intentionally small and exported at the top-level `mcp_tuning` package.

### Connect functions

- `connect_stdio(command, *, cwd=None, env=None) -> Client`
  - `command`: `list[str]` (recommended) or `str`
  - defaults to running the subprocess with the repo root as `cwd` (more reliable in notebooks)
- `connect_http(rpc_url, *, headers=None) -> Client`
- `connect_sse(*, sse_url, rpc_url, headers=None) -> Client`

### Client

`Client` (alias: `MCPClient`) is the main entry point for notebooks and scripts.

- Lifecycle
  - `close()`
  - `server_info() -> dict | None`

- Explore
  - `tools(timeout_s=30) -> list[ToolItem]`
  - `tool(name, timeout_s=30) -> ToolItem | None`
  - `resources(timeout_s=30) -> list[ResourceItem]`
  - `read_resource(uri, timeout_s=60) -> Any`
  - `prompts(timeout_s=30) -> list[PromptItem]`
  - `get_prompt(name, arguments=None, timeout_s=60) -> Any`

- Call
  - `call(name, arguments=None, timeout_s=60) -> CallResult`
  - `last() -> CallResult | None`

- Rendering (notebook-friendly)
  - `show(obj, mode='auto'|'json'|'text'|'markdown', compact=True, max_depth=5, max_items=60) -> None`
  - `dumps(obj, compact=True, max_depth=5, max_items=60) -> str`

- Cases (input-only: tool + args)
  - `save_case(tool, arguments, note=None, root=None) -> Path`
  - `cases(root=None) -> list[Path]`
  - `load_case(path) -> CallCase`
  - `replay_case(case, timeout_s=60) -> CallResult`
  - `replay_case_path(path, timeout_s=60) -> CallResult`

- Exports
  - `export_logs(root=None) -> Path`
  - `export_history(root=None) -> Path`
  - `export_last(root=None) -> Path`

### Models (data types)

The following types are also exported for type hints and inspection:

- `ToolItem`, `ResourceItem`, `PromptItem`
- `CallCase` (stores tool + args + metadata)
- `CallResult` (includes `ok/result/error/stderr_tail/ts`)
- `LogEvent`

## Files & Folders

- `examples/notebooks/`: example notebooks (script-first)
- `examples/servers/`: example MCP servers
- `docs/`: detailed documentation (start at `docs/index.md`)
- `cases/`: saved cases (`*.json`)
- `exports/`: exported logs/history/results (`*.json`)

## Troubleshooting

- Timeouts usually mean the server did not start correctly (missing deps, wrong executable, wrong paths).
  - For the FastMCP example, run the server with `.venv/Scripts/python.exe`.
- Notebook working directories are often not the repo root; this library defaults stdio subprocess `cwd` to the repo root.
- On timeouts, the error message includes a stderr tail (stdio) to help you debug server startup failures.

## Tests

```powershell
python -m pytest
```
