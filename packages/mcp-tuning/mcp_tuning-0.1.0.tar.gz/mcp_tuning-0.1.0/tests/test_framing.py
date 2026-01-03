from io import BytesIO

from mcp_tuning._mcp_stdio import _encode_lsp_message, _read_lsp_message


def test_lsp_message_roundtrip():
    payload = {"jsonrpc": "2.0", "id": 1, "method": "ping", "params": {"x": "y"}}
    data = _encode_lsp_message(payload)
    msg = _read_lsp_message(BytesIO(data))
    assert msg == payload
