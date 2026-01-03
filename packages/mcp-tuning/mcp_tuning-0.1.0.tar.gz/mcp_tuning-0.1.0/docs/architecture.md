# Architecture Overview

This project is designed around a small **public API** for script-first usage, with internal layers underneath.

## Public API (what most users need)

- `mcp_tuning.connect_stdio/connect_http/connect_sse`: create a connected client.
- `mcp_tuning.Client` (alias: `mcp_tuning.MCPClient`): synchronous client for explore/call/cases/exports.

## Internal layers (implementation details)

- `mcp_tuning.transports/*`: transport implementations (stdio/http/sse).
- `mcp_tuning._inspector.InspectorClient`: domain-level orchestration used by `Client`.

## Utility modules

- `mcp_tuning._rendering`: compact summaries + rich text/markdown extraction.
- `mcp_tuning._exporting`: JSON export helpers (writes under `exports/`).
- `mcp_tuning._mcp_protocol`: shared protocol payload helpers.
