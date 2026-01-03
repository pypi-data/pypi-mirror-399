import json
from pathlib import Path
from uuid import uuid4

from mcp_tuning._exporting import export_json, write_json
from mcp_tuning._mcp_protocol import default_initialize_params


def test_default_initialize_params_shape():
    params = default_initialize_params()
    assert params["protocolVersion"]
    assert params["clientInfo"]["name"]
    assert isinstance(params["capabilities"], dict)


def test_export_json_writes_file():
    root = Path("test-outputs") / f"export-{uuid4().hex[:10]}"
    root.mkdir(parents=True, exist_ok=True)
    path = export_json({"a": 1}, prefix="my payload", root=root)
    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8")) == {"a": 1}


def test_write_json_preserves_unicode():
    root = Path("test-outputs") / f"export-{uuid4().hex[:10]}"
    root.mkdir(parents=True, exist_ok=True)
    path = root / "x.json"
    write_json(path, {"msg": "中文"})
    assert "中文" in path.read_text(encoding="utf-8")
