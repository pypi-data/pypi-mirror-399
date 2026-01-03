from __future__ import annotations

import json
import shlex
from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal

from ._cases import list_cases, load_case
from ._inspector import InspectorClient
from .models import CallCase, CallResult, PromptItem, ResourceItem, ToolItem
from ._rendering import extract_rich_text, summarize


ViewMode = Literal["auto", "json", "text", "markdown"]


class Client:
    """
    Synchronous, script-first MCP client for notebooks and scripts.

    - Transport selection is done via the `connect_*()` helpers (in `mcp_tuning._api`).
    - Designed to work with MCP servers implemented in any language.
    """

    def __init__(self, inspector: InspectorClient) -> None:
        self._inspector = inspector
        self._last_call: CallResult | None = None
        self._tools_cache: list[ToolItem] | None = None

    @property
    def inspector(self) -> InspectorClient:
        return self._inspector

    def close(self) -> None:
        self._inspector.disconnect()

    def server_info(self) -> dict[str, Any] | None:
        return self._inspector.server_info()

    def tools(self, *, timeout_s: float = 30) -> list[ToolItem]:
        self._tools_cache = self._inspector.list_tools(timeout_s=timeout_s)
        return self._tools_cache

    def tool(self, name: str, *, timeout_s: float = 30) -> ToolItem | None:
        if self._tools_cache is None:
            self.tools(timeout_s=timeout_s)
        assert self._tools_cache is not None
        return next((t for t in self._tools_cache if t.name == name), None)

    def resources(self, *, timeout_s: float = 30) -> list[ResourceItem]:
        return self._inspector.list_resources(timeout_s=timeout_s)

    def read_resource(self, uri: str, *, timeout_s: float = 60) -> Any:
        return self._inspector.read_resource(uri, timeout_s=timeout_s)

    def prompts(self, *, timeout_s: float = 30) -> list[PromptItem]:
        return self._inspector.list_prompts(timeout_s=timeout_s)

    def get_prompt(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
        *,
        timeout_s: float = 60,
    ) -> Any:
        return self._inspector.get_prompt(name, arguments or {}, timeout_s=timeout_s)

    def call(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
        *,
        timeout_s: float = 60,
    ) -> CallResult:
        self._last_call = self._inspector.call_tool(
            name, arguments or {}, timeout_s=timeout_s
        )
        return self._last_call

    def last(self) -> CallResult | None:
        return self._last_call

    def save_case(
        self,
        tool: str,
        arguments: dict[str, Any],
        *,
        note: str | None = None,
        root: str | Path | None = None,
    ) -> Path:
        case = self._inspector.create_case(tool, arguments, note=note)
        return self._inspector.save_case(case, root=root)

    def cases(self, *, root: str | Path | None = None) -> list[Path]:
        return list_cases(root=root)

    def load_case(self, path: str | Path) -> CallCase:
        return load_case(path)

    def replay_case(self, case: CallCase, *, timeout_s: float = 60) -> CallResult:
        return self._inspector.call_tool(case.tool, case.arguments, timeout_s=timeout_s)

    def replay_case_path(
        self, path: str | Path, *, timeout_s: float = 60
    ) -> CallResult:
        return self.replay_case(self.load_case(path), timeout_s=timeout_s)

    def export_logs(self, *, root: str | Path | None = None) -> Path:
        return self._inspector.export_logs(root=root)

    def export_history(self, *, root: str | Path | None = None) -> Path:
        return self._inspector.export_history(root=root)

    def export_last(self, *, root: str | Path | None = None) -> Path:
        if self._last_call is None:
            raise RuntimeError("No last call result to export.")
        return self._inspector.export_payload(
            asdict(self._last_call), prefix=f"result-{self._last_call.tool}", root=root
        )

    def show(
        self,
        obj: Any,
        *,
        mode: ViewMode = "auto",
        compact: bool = True,
        max_depth: int = 5,
        max_items: int = 60,
    ) -> None:
        """
        Render an MCP response in a notebook-friendly way.

        - mode=auto: prefer markdown/text if present, otherwise JSON.
        - compact=True: summarize large payloads before JSON pretty-print.
        """
        try:
            from IPython.display import Markdown, display
        except Exception:
            print(
                self.dumps(
                    obj, compact=compact, max_depth=max_depth, max_items=max_items
                )
            )
            return

        render_mode: ViewMode = mode
        kind, text = extract_rich_text(obj)
        if mode == "auto":
            if kind == "markdown":
                render_mode = "markdown"
            elif kind == "text":
                render_mode = "text"
            elif isinstance(obj, str):
                render_mode = "text"
            else:
                render_mode = "json"

        if render_mode == "markdown":
            display(Markdown(text or ""))
            return
        if render_mode == "text":
            print(
                text
                if text is not None
                else (obj if isinstance(obj, str) else self.dumps(obj, compact=compact))
            )
            return
        print(
            self.dumps(obj, compact=compact, max_depth=max_depth, max_items=max_items)
        )

    def dumps(
        self,
        obj: Any,
        *,
        compact: bool = True,
        max_depth: int = 5,
        max_items: int = 60,
    ) -> str:
        payload = (
            summarize(obj, max_depth=max_depth, max_items=max_items) if compact else obj
        )
        return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


def parse_command(command: list[str] | str) -> list[str]:
    if isinstance(command, list):
        return command
    return shlex.split(command, posix=False)
