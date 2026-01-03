from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal


JsonObject = dict[str, Any]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ToolItem:
    name: str
    description: str | None = None
    input_schema: JsonObject | None = None


@dataclass(frozen=True)
class ResourceItem:
    uri: str
    name: str | None = None
    description: str | None = None
    mime_type: str | None = None


@dataclass(frozen=True)
class PromptItem:
    name: str
    description: str | None = None
    arguments_schema: JsonObject | None = None


@dataclass(frozen=True)
class LogEvent:
    ts: str
    direction: Literal["send", "recv"]
    message: JsonObject
    meta: JsonObject = field(default_factory=dict)


@dataclass(frozen=True)
class CallResult:
    ok: bool
    tool: str
    arguments: JsonObject
    result: Any | None = None
    error: str | None = None
    stderr_tail: list[str] = field(default_factory=list)
    ts: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class CallCase:
    id: str
    tool: str
    arguments: JsonObject
    created_at: str = field(default_factory=utc_now_iso)
    note: str | None = None
