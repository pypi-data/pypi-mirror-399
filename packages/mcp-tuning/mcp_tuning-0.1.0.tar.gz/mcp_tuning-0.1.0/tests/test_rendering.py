from mcp_tuning._rendering import extract_rich_text, summarize


def test_summarize_truncates_long_string():
    s = "a" * 50
    out = summarize(s, max_str=10)
    assert out.endswith("…")
    assert len(out) == 10


def test_summarize_limits_depth():
    obj = {"a": {"b": {"c": 1}}}
    out = summarize(obj, max_depth=2)
    assert out["a"]["b"] == "…"


def test_summarize_limits_list_items():
    obj = list(range(100))
    out = summarize(obj, max_items=3)
    assert out[:3] == [0, 1, 2]
    assert "more items" in out[-1]


def test_summarize_limits_dict_keys():
    obj = {f"k{i}": i for i in range(10)}
    out = summarize(obj, max_items=3)
    assert len([k for k in out.keys() if k != "…"]) == 3
    assert "more keys" in out["…"]


def test_extract_rich_text_from_content():
    obj = {"content": [{"type": "text", "text": "hello"}]}
    kind, text = extract_rich_text(obj)
    assert kind == "text"
    assert text == "hello"


def test_extract_rich_text_from_messages_markdown():
    obj = {
        "messages": [
            {"role": "user", "content": [{"type": "markdown", "text": "# hi"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "ok"}]},
        ]
    }
    kind, text = extract_rich_text(obj)
    assert kind == "markdown"
    assert "### user" in text
    assert "# hi" in text
