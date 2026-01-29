"""配置管理模块：配置加载/保存、优先级合并"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from msgspec import UNSET, Struct, UnsetType, structs
from msgspec import json as msgjson

from .constants import CONFIG_FILE


class Config(Struct, omit_defaults=True):
    """用户配置，保存到配置文件。

    Attributes:
        username: 校园网账号。
        password: 校园网密码。
        interval: 检测间隔（分钟）。
    """

    username: str | UnsetType = UNSET
    password: str | UnsetType = UNSET
    interval: int | UnsetType = UNSET

    @classmethod
    def load_from_json(cls, file_path: str | Path) -> Config:
        """从 JSON 文件加载配置，文件不存在时返回空配置。"""
        try:
            bytes = Path(file_path).read_bytes()
            return msgjson.decode(bytes, type=Config)
        except FileNotFoundError:
            return cls()

    def save_to_json(self, file_path: Path | str) -> int:
        """保存当前配置到 JSON 文件。"""
        bytes = msgjson.encode(self) + b"\n"
        return Path(file_path).write_bytes(bytes)

    def to_dict(self) -> dict[str, Any]:
        """导出为字典（过滤 UNSET 值）。"""
        return {k: v for k, v in structs.asdict(self).items() if v is not UNSET}


# 全局配置实例
config = Config.load_from_json(CONFIG_FILE)
