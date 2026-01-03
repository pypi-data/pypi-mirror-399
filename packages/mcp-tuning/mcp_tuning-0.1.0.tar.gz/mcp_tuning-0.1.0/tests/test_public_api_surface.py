import mcp_tuning


def test_public_api_surface_is_small():
    assert hasattr(mcp_tuning, "connect_stdio")
    assert hasattr(mcp_tuning, "connect_http")
    assert hasattr(mcp_tuning, "connect_sse")
    assert hasattr(mcp_tuning, "Client")
    assert hasattr(mcp_tuning, "MCPClient")

    # Internal building blocks should not be promoted at top-level.
    assert not hasattr(mcp_tuning, "InspectorClient")
    assert not hasattr(mcp_tuning, "Transport")

