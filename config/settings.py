from __future__ import annotations

import os
from pathlib import Path


def _get_base_data_dir() -> Path:
    """获取应用数据根目录（跨平台，适合打包后使用）。"""
    # 优先使用环境变量（方便打包或自定义）
    env_path = os.getenv("IN_OUT_DATA_DIR")
    if env_path:
        return Path(env_path).expanduser().resolve()

    # Windows 上使用 LOCALAPPDATA，其它平台使用家目录下的隐藏目录
    if os.name == "nt":
        local_appdata = os.getenv("LOCALAPPDATA") or str(Path.home())
        return Path(local_appdata) / "InOutInventory"
    return Path.home() / ".in_out_inventory"


DATA_DIR: Path = _get_base_data_dir() / "data"
EXPORT_DIR: Path = _get_base_data_dir() / "exports"

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

DB_FILE: Path = DATA_DIR / "inventory.db"

