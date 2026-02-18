from __future__ import annotations

from pathlib import Path


def _get_project_root() -> Path:
    """返回项目根目录（以当前文件所在目录向上两级推断）。"""
    return Path(__file__).resolve().parents[1]


PROJECT_ROOT: Path = _get_project_root()
DATA_DIR: Path = PROJECT_ROOT / "data"
EXPORT_DIR: Path = PROJECT_ROOT / "exports"

# 确保目录存在（开发阶段默认使用项目内目录）
DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

DB_FILE: Path = DATA_DIR / "inventory.db"

