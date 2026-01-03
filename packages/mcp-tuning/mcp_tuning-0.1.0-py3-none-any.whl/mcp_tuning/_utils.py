from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path


def safe_filename(value: str, *, max_len: int = 80) -> str:
    s = value.strip()
    s = re.sub(r"[^a-zA-Z0-9._-]+", "-", s)
    s = s[:max_len] if s else "file"
    return s


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def exports_dir(root: str | Path | None = None) -> Path:
    base = Path(root) if root is not None else Path.cwd()
    return base / "exports"

