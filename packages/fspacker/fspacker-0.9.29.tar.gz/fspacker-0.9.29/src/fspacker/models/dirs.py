from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel
from pydantic import Field
from pydantic_settings import SettingsConfigDict

__all__ = ["DEFAULT_CACHE_DIR", "Dirs"]

# cache settings
DEFAULT_CACHE_DIR = Path("~").expanduser() / ".cache" / "fspacker"


class Dirs(BaseModel):
    """目录配置."""

    model_config = SettingsConfigDict(extra="allow")

    cache: Path = Field(default_factory=lambda: DEFAULT_CACHE_DIR)
    embed: Path = Field(
        default_factory=lambda: DEFAULT_CACHE_DIR / "embed-repo",
    )
    libs: Path = Field(default_factory=lambda: DEFAULT_CACHE_DIR / "libs-repo")
    tools: Path = Field(default_factory=lambda: DEFAULT_CACHE_DIR / "tools")
    checksum: str = ""

    def __str__(self) -> str:
        """字符串化.

        Returns:
            str: 字符串.
        """
        dirs = {
            "cache": self.cache,
            "embed": self.embed,
            "libs": self.libs,
            "tools": self.tools,
        }
        return ",".join([f"{k}={v}" for k, v in dirs.items()])

    @property
    def entries(self) -> tuple[Path, Path, Path]:
        """获取所有目录.

        Returns:
            tuple[Path, Path, Path]: 所有目录
        """
        return (self.cache, self.embed, self.libs)
