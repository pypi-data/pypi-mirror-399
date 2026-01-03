# Notebook Scripting Guide (recommended)

This project is intended to be used from notebook **code cells** (script-first), not as a GUI.

## Connect (stdio, recommended)

```python
from mcp_tuning import connect_stdio

# You can pass either a list argv (recommended) or a string command.
# Note: the helper runs the subprocess from the repo root so relative paths work.
c = connect_stdio([".venv/Scripts/python.exe", "examples/servers/simple_stdio_server.py"])
c.server_info()
```

If you prefer `uv run`, this also works, but may be restricted in some environments:

```python
c = connect_stdio("uv run python examples/servers/simple_stdio_server.py")
```

## If you see timeouts: verify you're importing the local code

In notebooks, imports may accidentally resolve to an older installed `mcp_tuning` instead of the workspace `src/`.

Run:

```python
import mcp_tuning, sys
print(sys.executable)
print(mcp_tuning.__file__)
```

If `mcp_tuning.__file__` is not under your repo `src/mcp_tuning/`, add `src/` to `sys.path` or restart Jupyter from the repo root.

## Explore

```python
c.tools()
c.resources()
c.prompts()
```

## Call tools

```python
r = c.call("add", {"a": 1, "b": 2})
r.ok, r.result, r.error
```

## Render results

```python
c.show(r.result)                 # auto markdown/text/json
print(c.dumps(r.result))         # json string (compact by default)
print(c.dumps(r.result, compact=False))
```

## Save inputs as cases (tool + args)

```python
case_path = c.save_case("add", {"a": 10, "b": 20}, note="basic add test")
case_path
```

## Export logs/history/last result

```python
c.export_logs()
c.export_history()
c.export_last()
```

## Cleanup

```python
c.close()
```
