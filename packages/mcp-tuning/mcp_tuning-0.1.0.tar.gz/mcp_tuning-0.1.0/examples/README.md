# Examples

This folder contains runnable examples for learning and for quick manual testing.

## 1) Simple stdio MCP server

`examples/servers/simple_stdio_server.py` is a minimal MCP server that exposes a few tools and optional resources/prompts.

Run it directly:

```powershell
.venv\\Scripts\\python.exe examples/servers/simple_stdio_server.py
```

Then connect to it from the notebook UI:

- Open `examples/notebooks/01_mcp_inspector_demo.ipynb`
- Start JupyterLab: `uv run jupyter lab`
- Set Transport to `stdio`
- Command: `.venv\\Scripts\\python.exe examples/servers/simple_stdio_server.py`

## Notebooks

- `examples/notebooks/01_mcp_inspector_demo.ipynb`: script-first quick tour
- `examples/notebooks/02_stdio_deep_dive.ipynb`: deeper stdio validation and logs
- `examples/notebooks/03_cases_replay_exports.ipynb`: cases + replay + exports
- `examples/notebooks/04_http_sse_local_test_server.ipynb`: local HTTP/SSE transport sanity checks

## 2) Use the built-in mock server (tests)

The test/mock server lives in `src/mcp_tuning/_mock_server.py` and is used by unit/integration tests.

```powershell
$env:PYTHONPATH='src'
python src/mcp_tuning/_mock_server.py
```
