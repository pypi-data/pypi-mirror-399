from __future__ import annotations

from typing import Any


def default_initialize_params(
    *,
    protocol_version: str = "2024-11-05",
    client_name: str = "mcp-tuning",
    client_version: str = "0.1.0",
    capabilities: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "protocolVersion": protocol_version,
        "clientInfo": {"name": client_name, "version": client_version},
        "capabilities": capabilities or {},
    }

