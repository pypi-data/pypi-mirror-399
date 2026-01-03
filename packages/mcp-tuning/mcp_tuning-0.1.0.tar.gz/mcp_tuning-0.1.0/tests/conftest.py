import os
import sys
from pathlib import Path


def pytest_configure():
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    repo_root = Path(__file__).resolve().parents[1]
    src = repo_root / "src"
    sys.path.insert(0, str(src))
    (repo_root / "test-outputs").mkdir(parents=True, exist_ok=True)
