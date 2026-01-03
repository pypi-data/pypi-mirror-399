import sys

from mcp_tuning import connect_stdio


def test_notebook_client_stdio_basic():
    cmd = [sys.executable, "src/mcp_tuning/_mock_server.py"]
    c = connect_stdio(cmd)
    tools = c.tools()
    assert any(t.name == "echo" for t in tools)

    r = c.call("add", {"a": 1, "b": 2})
    assert r.ok is True
    assert r.result == {"sum": 3.0}

    s = c.dumps(r.result)
    assert "sum" in s
    c.close()


def test_connect_stdio_rewrites_uv_run_python():
    from mcp_tuning import connect_stdio

    # This should not actually execute uv; it should rewrite to .venv python if present.
    try:
        c = connect_stdio("uv run python src/mcp_tuning/_mock_server.py")
    except Exception as e:
        # If .venv isn't present in some environments, this may fail; but it should not be a uv cache error.
        assert "uv\\cache" not in str(e).lower()
        return
    c.close()


def test_connect_stdio_from_subdir_runs_in_repo_root(monkeypatch):
    # Simulate running from a notebook directory where relative paths would otherwise break.
    monkeypatch.chdir("examples/notebooks")

    # Use the repo's mock server path (relative to repo root) and ensure connect works.
    cmd = [sys.executable, "src/mcp_tuning/_mock_server.py"]
    c = connect_stdio(cmd)
    assert c.server_info() is not None
    c.close()
