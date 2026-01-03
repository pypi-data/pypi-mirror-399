
"""Internal orchestration layer for the public `Client` API."""
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
from typing import Any
from uuid import uuid4

from ._cases import load_case, save_case
from ._exporting import export_json, write_json
from ._mcp_protocol import default_initialize_params
from ._mcp_stdio import MCPProtocolError
from ._utils import ensure_dir, exports_dir, safe_filename, utc_stamp
from .models import CallCase, CallResult, LogEvent, PromptItem, ResourceItem, ToolItem
from .transports import HttpTransport, SseTransport, StdioTransport, Transport


def _as_dict(obj: Any) -> dict[str, Any] | None:
    return obj if isinstance(obj, dict) else None


def _as_list(obj: Any) -> list[Any] | None:
    return obj if isinstance(obj, list) else None


def _init_payload() -> dict[str, Any]:
    return default_initialize_params()


class InspectorClient:
    def __init__(self) -> None:
        self._transport: Transport | None = None
        self._history: list[CallResult] = []

    def connect(self, command: list[str] | str) -> dict[str, Any] | None:
        return self.connect_stdio(command)

    def connect_stdio(
        self,
        command: list[str] | str,
        *,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any] | None:
        self.disconnect()
        self._transport = StdioTransport(command, cwd=cwd, env=env)
        self._transport.start()
        info = self._transport.request("initialize", _init_payload(), timeout_s=30)
        self._transport.notify("initialized")
        return info if isinstance(info, dict) else None

    def connect_http(
        self, rpc_url: str, *, headers: dict[str, str] | None = None
    ) -> dict[str, Any] | None:
        self.disconnect()
        self._transport = HttpTransport(rpc_url, headers=headers)
        self._transport.start()
        info = self._transport.request("initialize", _init_payload(), timeout_s=30)
        self._transport.notify("initialized")
        return info if isinstance(info, dict) else None

    def connect_sse(
        self,
        *,
        sse_url: str,
        rpc_url: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any] | None:
        self.disconnect()
        self._transport = SseTransport(
            sse_url=sse_url, rpc_url=rpc_url, headers=headers
        )
        self._transport.start()
        info = self._transport.request("initialize", _init_payload(), timeout_s=30)
        self._transport.notify("initialized")
        return info if isinstance(info, dict) else None

    def disconnect(self) -> None:
        if self._transport is None:
            return
        self._transport.close()
        self._transport = None

    def is_connected(self) -> bool:
        return self._transport is not None and self._transport.is_running()

    def stderr_tail(self, n: int = 50) -> list[str]:
        if self._transport is None:
            return []
        return self._transport.stderr_tail(n)

    def events_tail(self, n: int = 200) -> list[LogEvent]:
        if self._transport is None:
            return []
        return self._transport.events_tail(n)

    def history_tail(self, n: int = 50) -> list[CallResult]:
        if n <= 0:
            return []
        return self._history[-n:]

    def clear_history(self) -> None:
        self._history.clear()

    def server_info(self) -> dict[str, Any] | None:
        if self._transport is None:
            return None
        return self._transport.server_info()

    def list_tools(self, *, timeout_s: float | None = None) -> list[ToolItem]:
        if self._transport is None:
            raise RuntimeError("Not connected")
        result = self._transport.request("tools/list", {}, timeout_s=timeout_s or 30)
        obj = _as_dict(result)
        tools = obj.get("tools") if obj is not None else result
        items = _as_list(tools) or []
        parsed: list[ToolItem] = []
        for t in items:
            d = _as_dict(t)
            if not d or "name" not in d:
                continue
            parsed.append(
                ToolItem(
                    name=str(d["name"]),
                    description=d.get("description"),
                    input_schema=d.get("inputSchema") or d.get("input_schema"),
                )
            )
        return parsed

    def list_resources(self, *, timeout_s: float | None = None) -> list[ResourceItem]:
        if self._transport is None:
            raise RuntimeError("Not connected")
        result = self._transport.request(
            "resources/list", {}, timeout_s=timeout_s or 30
        )
        obj = _as_dict(result)
        resources = obj.get("resources") if obj is not None else result
        items = _as_list(resources) or []
        parsed: list[ResourceItem] = []
        for r in items:
            d = _as_dict(r)
            if not d or "uri" not in d:
                continue
            parsed.append(
                ResourceItem(
                    uri=str(d["uri"]),
                    name=d.get("name"),
                    description=d.get("description"),
                    mime_type=d.get("mimeType") or d.get("mime_type"),
                )
            )
        return parsed

    def read_resource(self, uri: str, *, timeout_s: float | None = None) -> Any:
        if self._transport is None:
            raise RuntimeError("Not connected")
        return self._transport.request(
            "resources/read", {"uri": uri}, timeout_s=timeout_s or 60
        )

    def list_prompts(self, *, timeout_s: float | None = None) -> list[PromptItem]:
        if self._transport is None:
            raise RuntimeError("Not connected")
        result = self._transport.request("prompts/list", {}, timeout_s=timeout_s or 30)
        obj = _as_dict(result)
        prompts = obj.get("prompts") if obj is not None else result
        items = _as_list(prompts) or []
        parsed: list[PromptItem] = []
        for p in items:
            d = _as_dict(p)
            if not d or "name" not in d:
                continue
            parsed.append(
                PromptItem(
                    name=str(d["name"]),
                    description=d.get("description"),
                    arguments_schema=d.get("argumentsSchema")
                    or d.get("arguments_schema"),
                )
            )
        return parsed

    def get_prompt(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
        *,
        timeout_s: float | None = None,
    ) -> Any:
        if self._transport is None:
            raise RuntimeError("Not connected")
        return self._transport.request(
            "prompts/get",
            {"name": name, "arguments": arguments or {}},
            timeout_s=timeout_s or 60,
        )

    def call_tool(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
        *,
        timeout_s: float | None = None,
    ) -> CallResult:
        if self._transport is None:
            raise RuntimeError("Not connected")
        args = dict(arguments or {})
        try:
            result = self._transport.request(
                "tools/call",
                {"name": name, "arguments": args},
                timeout_s=timeout_s or 60,
            )
            cr = CallResult(
                ok=True,
                tool=name,
                arguments=args,
                result=result,
                stderr_tail=self.stderr_tail(),
            )
            self._history.append(cr)
            return cr
        except Exception as e:
            message = str(e)
            if isinstance(e, MCPProtocolError) and e.args:
                message = str(e.args[0])
            cr = CallResult(
                ok=False,
                tool=name,
                arguments=args,
                error=message,
                stderr_tail=self.stderr_tail(),
            )
            self._history.append(cr)
            return cr

    def create_case(
        self, tool: str, arguments: dict[str, Any], *, note: str | None = None
    ) -> CallCase:
        case_id = f"{safe_filename(tool)}-{uuid4().hex[:10]}"
        return CallCase(id=case_id, tool=tool, arguments=dict(arguments), note=note)

    def save_case(self, case: CallCase, root: str | Path | None = None) -> Path:
        return save_case(case, root=root)

    def load_case(self, path: str | Path) -> CallCase:
        return load_case(path)

    def replay_case(self, case: CallCase) -> CallResult:
        return self.call_tool(case.tool, case.arguments)

    def export_case_dict(self, case: CallCase) -> dict[str, Any]:
        return asdict(case)

    def export_logs(self, root: str | Path | None = None) -> Path:
        d = ensure_dir(exports_dir(root))
        path = d / f"logs-{utc_stamp()}.json"
        events = self.events_tail(10_000)
        payload = [asdict(e) for e in events]
        return write_json(path, payload)

    def export_history(self, root: str | Path | None = None) -> Path:
        d = ensure_dir(exports_dir(root))
        path = d / f"history-{utc_stamp()}.json"
        payload = [asdict(h) for h in self.history_tail(10_000)]
        return write_json(path, payload)

    def export_payload(
        self, payload: Any, *, prefix: str = "payload", root: str | Path | None = None
    ) -> Path:
        return export_json(payload, prefix=prefix, root=root)

