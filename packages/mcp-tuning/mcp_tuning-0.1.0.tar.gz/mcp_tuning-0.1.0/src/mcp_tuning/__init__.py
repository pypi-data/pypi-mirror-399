"""
mcp-tuning: script-first MCP client for notebooks and scripts.

Public entry points:

```python
from mcp_tuning import connect_stdio

c = connect_stdio([".venv/Scripts/python.exe", "src/mcp_tuning/_mock_server.py"])
print([t.name for t in c.tools()])
print(c.call("add", {"a": 1, "b": 2}).result)
c.close()
```

The API is intentionally small:
- `connect_stdio/connect_http/connect_sse` to create a client
- `MCPClient` (aka `Client`) for explore/call/cases/exports
"""

from .__about__ import __version__
from ._api import connect_http, connect_sse, connect_stdio
from .client import Client
from .models import CallCase, CallResult, LogEvent, PromptItem, ResourceItem, ToolItem

MCPClient = Client

__all__ = [
    "__version__",
    "MCPClient",
    "Client",
    "connect_stdio",
    "connect_http",
    "connect_sse",
    "ToolItem",
    "ResourceItem",
    "PromptItem",
    "CallCase",
    "CallResult",
    "LogEvent",
]
