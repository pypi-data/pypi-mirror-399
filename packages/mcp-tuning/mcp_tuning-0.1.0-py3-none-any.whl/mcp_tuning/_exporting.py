from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ._utils import ensure_dir, exports_dir, safe_filename, utc_stamp


def write_json(path: Path, payload: Any) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    return path


def export_json(payload: Any, *, prefix: str, root: str | Path | None = None) -> Path:
    d = ensure_dir(exports_dir(root))
    path = d / f"{safe_filename(prefix)}-{utc_stamp()}.json"
    return write_json(path, payload)
