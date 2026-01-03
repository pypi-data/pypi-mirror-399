# Transports

Transports are selected via the public connect helpers:

- `connect_stdio(...)`: JSON-RPC over stdio (subprocess, JSON-lines framing)
- `connect_http(...)`: JSON-RPC over HTTP POST
- `connect_sse(...)`: JSON-RPC over HTTP POST + SSE stream

(Transport classes exist for advanced use, but are not required for normal usage.)

## Configuration in the notebook UI

- Transport `stdio`:
  - Command: e.g. `python examples/servers/simple_stdio_server.py`
- Transport `http`:
  - RPC URL: e.g. `http://localhost:8000/rpc`
  - Headers (JSON): e.g. `{"Authorization": "Bearer ..."}`
- Transport `sse`:
  - RPC URL: where POST requests go
  - SSE URL: where events are streamed
  - Headers (JSON): applied to both requests

## Notes

- Real-world MCP HTTP/SSE deployments may differ in endpoints and framing; treat HTTP/SSE here as an extensible baseline.
- If a server does not support `resources/*` or `prompts/*`, those calls will fail; use the Logs tab to debug.

