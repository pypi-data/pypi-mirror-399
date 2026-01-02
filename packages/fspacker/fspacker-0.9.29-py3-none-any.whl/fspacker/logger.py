from __future__ import annotations

import logging
import platform
from functools import wraps
from typing import Callable
from typing import TypeVar

from rich.logging import RichHandler
from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


__all__ = ["logger"]


class _Logger:
    """日志记录器."""

    sep_char = "="
    sep_length = 40

    _logger: logging.Logger | None = None
    _instance: _Logger | None = None

    info: Callable[..., None]
    warning: Callable[..., None]
    debug: Callable[..., None]
    error: Callable[..., None]
    critical: Callable[..., None]
    exception: Callable[..., None]

    @classmethod
    def get_instance(cls, name: str) -> _Logger:
        """获取日志记录器实例.

        Args:
            name (str): 模块名称.

        Returns:
            logging.Logger: 日志记录器实例.
        """
        if cls._logger is None:
            logging.basicConfig(
                level=logging.INFO,
                format="[%(asctime)s] %(message)s",
                datefmt="%X",
                handlers=[RichHandler(markup=True)],
            )

            cls._logger = logging.getLogger(name)
            cls._instance = _Logger()

            cls._instance.info = cls._logger.info
            cls._instance.warning = cls._logger.warning
            cls._instance.debug = cls._logger.debug
            cls._instance.error = cls._logger.error
            cls._instance.critical = cls._logger.critical
            cls._instance.exception = cls._logger.exception

        assert cls._instance
        return cls._instance

    def set_debug_mode(self, *, debug_mode: bool) -> None:
        """设置日志记录模式.

        Args:
            debug_mode (bool): 是否开启调试模式.
        """
        assert self._logger

        from fspacker.settings import settings  # noqa: PLC0415

        settings.mode.debug = debug_mode
        self._logger.setLevel(
            logging.DEBUG if debug_mode else logging.INFO,
        )

    def show_build_info(self, func: Callable[P, R]) -> Callable[P, R]:
        """显示构建信息.

        Returns:
            Callable[P, R]: 包装后的函数.
        """

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            from fspacker import __build_date__  # noqa: PLC0415
            from fspacker import __version__  # noqa: PLC0415

            assert self._logger

            self.show_sep_msg("FSPACKER")
            self._logger.info(
                f"版本: {__version__}, 构建日期: {__build_date__}",
            )
            self._logger.info(f"Python 版本: {platform.python_version()}")
            self._logger.info(
                f"操作系统: {platform.system()} {platform.release()}",
            )
            self.show_sep_msg("FSPACKER")

            return func(*args, **kwargs)

        return wrapper

    def show_settings_mode(self) -> None:
        """显示设置模式."""
        assert self._logger

        from fspacker.settings import settings  # noqa: PLC0415

        self._logger.info(f"模式: {settings.mode}")
        self._logger.info(f"链接: {settings.urls}")
        self._logger.info(f"目录: {settings.dirs}")

    def show_sep_msg(self, sep_msg: str) -> None:
        """显示分隔符信息.

        Args:
            sep_msg (str): 分隔符内容.
        """
        assert self._logger

        self._logger.info(
            self.sep_char * self.sep_length
            + sep_msg
            + self.sep_char * self.sep_length,
        )


# 日志记录器实例, 模块级单例
logger = _Logger.get_instance(__name__)
