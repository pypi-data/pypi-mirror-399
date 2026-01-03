from __future__ import annotations

from collections.abc import Mapping, Sequence, Set as AbstractSet
from itertools import islice
from typing import Any


def summarize(
    obj: Any,
    *,
    max_depth: int = 5,
    max_items: int = 60,
    max_str: int = 4000,
    _seen: set[int] | None = None,
) -> Any:
    """
    遞歸地摘要物件結構，具備循環引用檢測與記憶體優化。
    """
    # 1. 基礎檢查
    if max_depth <= 0:
        return "…"
    
    # 2. 簡單類型直接返回
    if obj is None or isinstance(obj, (bool, int, float)):
        return obj

    # 3. 循環引用檢測
    if _seen is None:
        _seen = set()
    
    obj_id = id(obj)
    if obj_id in _seen:
        return "… (recursion)"
    
    # 4. 字串截斷
    if isinstance(obj, str):
        if len(obj) <= max_str:
            return obj
        return obj[: max_str - 1] + "…"

    # 準備遞歸參數
    next_kwargs = {
        "max_depth": max_depth - 1,
        "max_items": max_items,
        "max_str": max_str,
        "_seen": _seen,
    }

    _seen.add(obj_id)
    try:
        # 5. 處理字典 (Mapping)
        if isinstance(obj, Mapping):
            out: dict[str, Any] = {}
            # 使用 islice 避免在記憶體中創建巨大的 items 列表
            for k, v in islice(obj.items(), max_items):
                out[str(k)] = summarize(v, **next_kwargs)
            
            if len(obj) > max_items:
                out["…"] = f"({len(obj) - max_items} more keys)"
            return out

        # 6. 處理列表、元組、集合 (Sequence / Set)
        # 排除 str 和 bytes，因為它們也是 Sequence
        if isinstance(obj, (Sequence, AbstractSet)) and not isinstance(obj, (str, bytes)):
            # 對於 Set，先轉為 iterator
            iterator = iter(obj)
            head = [summarize(x, **next_kwargs) for x in islice(iterator, max_items)]
            
            if len(obj) > max_items:
                head.append(f"… ({len(obj) - max_items} more items)")
            return head

    finally:
        _seen.remove(obj_id)

    # 7. 其他類型
    return str(obj)


def _parse_content_list(content: list[Any]) -> tuple[str, list[str]] | None:
    """
    輔助函數：從 content 列表中提取文本部分。
    返回 (kind, parts_list) 或 None。
    """
    parts: list[str] = []
    kind = "text"
    
    for item in content:
        if not isinstance(item, dict):
            continue
        
        t = item.get("type")
        if t == "markdown":
            kind = "markdown"
            
        if t in ("text", "markdown"):
            text_val = item.get("text")
            if isinstance(text_val, str):
                parts.append(text_val)
                
    if not parts:
        return None
    return kind, parts


def extract_rich_text(obj: Any) -> tuple[str | None, str | None]:
    """
    從複雜物件中提取富文本內容 (Markdown 或 Text)。
    """
    # Case 0: 直接是字串
    if isinstance(obj, str):
        return "text", obj
        
    if not isinstance(obj, dict):
        return None, None

    # Case 1: 處理 "content" 字段
    content = obj.get("content")
    if isinstance(content, list):
        result = _parse_content_list(content)
        if result:
            kind, parts = result
            return kind, "\n".join(parts)

    # Case 2: 處理 "messages" 字段
    messages = obj.get("messages")
    if isinstance(messages, list):
        lines: list[str] = []
        
        for m in messages:
            if not isinstance(m, dict):
                continue
            
            # 添加角色標頭
            role = m.get("role", "unknown")
            lines.append(f"### {role}")
            
            # 提取消息內容
            msg_content = m.get("content")
            if isinstance(msg_content, list):
                result = _parse_content_list(msg_content)
                if result:
                    _, parts = result
                    lines.extend(parts)
        
        if lines:
            return "markdown", "\n\n".join(lines)

    return None, None
