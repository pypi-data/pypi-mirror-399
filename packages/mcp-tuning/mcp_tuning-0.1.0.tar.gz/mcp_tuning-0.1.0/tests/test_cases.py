from pathlib import Path
from uuid import uuid4

from mcp_tuning._inspector import InspectorClient


def test_case_save_and_load():
    client = InspectorClient()
    case = client.create_case("echo", {"x": 1}, note="n")
    out = Path("test-outputs") / f"cases-{uuid4().hex[:10]}"
    out.mkdir(parents=True, exist_ok=True)
    path = client.save_case(case, root=out)
    loaded = client.load_case(path)
    assert loaded.tool == "echo"
    assert loaded.arguments == {"x": 1}
