import sys
from pathlib import Path
from uuid import uuid4

from mcp_tuning._inspector import InspectorClient


def _out_dir(name: str) -> Path:
    d = Path("test-outputs") / f"{name}-{uuid4().hex[:10]}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def test_inspector_connect_explore_call_and_logs():
    client = InspectorClient()
    info = client.connect_stdio([sys.executable, "src/mcp_tuning/_mock_server.py"])
    assert info is None or isinstance(info, dict)

    tools = client.list_tools()
    assert any(t.name == "echo" for t in tools)

    resources = client.list_resources()
    assert any(r.uri == "mock://hello.txt" for r in resources)

    prompts = client.list_prompts()
    assert any(p.name == "hello" for p in prompts)

    call = client.call_tool("add", {"a": 1, "b": 2})
    assert call.ok is True
    assert call.result == {"sum": 3.0}

    events = client.events_tail(200)
    assert any(e.direction == "send" and e.message.get("method") == "tools/call" for e in events)
    recv = [e for e in events if e.direction == "recv"]
    assert any("duration_ms" in (e.meta or {}) for e in recv)

    out = _out_dir("exports")
    logs_path = client.export_logs(root=out)
    history_path = client.export_history(root=out)
    assert logs_path.exists()
    assert history_path.exists()
    assert logs_path.read_text(encoding="utf-8").strip().startswith("[")
    assert history_path.read_text(encoding="utf-8").strip().startswith("[")

    client.disconnect()
