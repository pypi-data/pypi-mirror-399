from __future__ import annotations

import platform
from pathlib import Path
from typing import Set

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from fspacker.models.dirs import DEFAULT_CACHE_DIR
from fspacker.models.dirs import Dirs
from fspacker.models.mode import PackMode
from fspacker.models.urls import Urls

__all__ = ["settings"]

_env_filepath = DEFAULT_CACHE_DIR / ".env"
_export_prefixes = {"urls", "dirs"}


class _Settings(BaseSettings):
    """Settings for fspacker."""

    model_config = SettingsConfigDict(
        env_file=str(_env_filepath),
        env_prefix="FSP_",
        env_nested_delimiter="__",
        extra="allow",
    )

    MAX_THREAD: int = 24  # 构建最大线程数

    is_windows: bool = platform.system() == "Windows"
    is_linux: bool = platform.system() == "Linux"
    is_macos: bool = platform.system() == "Darwin"

    dirs: Dirs = Field(default_factory=Dirs)
    urls: Urls = Urls()
    mode: PackMode = PackMode()

    fsp_dir: Path = Path(__file__).parent
    src_dir: Path = fsp_dir.parent
    fsp_project_dir: Path = src_dir.parent
    assets_dir: Path = fsp_dir / "assets"
    python_exe: str = (
        "python.exe" if platform.system() == "Windows" else "python3"
    )
    ignore_folders: Set[str] = {
        "dist-info",
        "__pycache__",
        "__pypackages__",
        "site-packages",
        "runtime",
        "dist",
        ".venv",
        # node 库
        "node_modules",
    }
    # 窗口程序库
    gui_libs: Set[str] = {
        "PySide2",
        "PyQt5",
        "pygame",
        "matplotlib",
        "tkinter",
        "pandas",
        "pywebview",
        "webview",
    }
    # 使用tk的库
    tk_libs: Set[str] = {"matplotlib", "tkinter", "pandas"}
    # qt库
    qt_libs: Set[str] = {"PySide2", "PyQt5", "PySide6", "PyQt6"}

    def dump(self) -> None:
        """导出环境变量."""
        prefix = self.model_config.get("env_prefix")

        with _env_filepath.open("w", encoding="utf-8") as f:
            for name, value in self.model_dump(by_alias=True).items():
                if str(name) in _export_prefixes:
                    if isinstance(value, dict):
                        for sub_key, sub_val in value.items():
                            env_name = f"{name.upper()}__{sub_key.upper()}"
                            f.write(f"{prefix}{env_name}={sub_val}\n")
                    else:
                        f.write(f"{prefix}{name.upper()}={value}\n")


settings = _Settings()

for directory in settings.dirs.entries:
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
