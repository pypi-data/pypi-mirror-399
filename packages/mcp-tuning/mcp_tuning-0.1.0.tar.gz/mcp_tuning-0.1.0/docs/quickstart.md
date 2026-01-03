# Quickstart

## Install

```powershell
uv sync
uv sync --extra notebook --extra test
```

## Run JupyterLab

```powershell
uv run jupyter lab
```

Open `examples/notebooks/01_mcp_inspector_demo.ipynb`.

Recommended: follow `docs/notebook-scripting.md` for the script-first workflow.

## Connect to a demo server (stdio)

1. Start the example server:

```powershell
python examples/servers/simple_stdio_server.py
```

2. In the notebook UI:
   - Transport: `stdio`
   - Command: `python examples/servers/simple_stdio_server.py`
   - Click Connect, then Explore/Call.

## Run tests

```powershell
python -m pytest
```
