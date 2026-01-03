from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import CallCase


def cases_dir(root: str | Path | None = None) -> Path:
    base = Path(root) if root is not None else Path.cwd()
    return base / "cases"


def ensure_cases_dir(root: str | Path | None = None) -> Path:
    d = cases_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    return d


def case_path(case_id: str, root: str | Path | None = None) -> Path:
    return cases_dir(root) / f"{case_id}.json"


def save_case(case: CallCase, root: str | Path | None = None) -> Path:
    ensure_cases_dir(root)
    path = case_path(case.id, root)
    payload = asdict(case)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_case(path: str | Path) -> CallCase:
    p = Path(path)
    obj: dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
    return CallCase(
        id=str(obj["id"]),
        tool=str(obj["tool"]),
        arguments=dict(obj.get("arguments") or {}),
        created_at=str(obj.get("created_at") or obj.get("createdAt") or ""),
        note=obj.get("note"),
    )


def list_cases(root: str | Path | None = None) -> list[Path]:
    d = cases_dir(root)
    if not d.exists():
        return []
    return sorted(d.glob("*.json"), key=lambda p: p.name)

