# Writing Simple MCP Servers

For local testing, the easiest starting point is a stdio server.

## Minimal stdio server

See `examples/servers/simple_stdio_server.py` for a complete runnable example built with `mcp.server.fastmcp.FastMCP`. It demonstrates:

- `initialize` / `initialized`
- `tools/list` / `tools/call`
- optional `resources/list` / `resources/read`
- optional `prompts/list` / `prompts/get`

## Tips

- Always reply to requests with the same `id`.
- When debugging, print diagnostics to stderr; the notebook UI shows a stderr tail on errors (stdio only).
- Keep tools deterministic where possible so cases are reproducible.

## Running the example with uv

```powershell
uv run python examples/servers/simple_stdio_server.py
```
