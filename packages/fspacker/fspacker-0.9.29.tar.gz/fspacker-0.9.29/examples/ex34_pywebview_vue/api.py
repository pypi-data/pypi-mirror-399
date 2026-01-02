from __future__ import annotations

import platform
import sys
from typing import Any
from typing import Optional
from typing import Sequence

import webview


class BaseApi:
    """基础API."""


class SystemApi(BaseApi):
    """系统API."""

    def show_notification(self, title: str, body: str) -> None:
        """显示系统通知."""
        print(f"通知: {title} - {body}")

    def minimize_window(self) -> None:
        """最小化窗口."""
        try:
            webview.windows[0].minimize()
        except AttributeError as e:
            print(f"最小化窗口失败: {e}")
        else:
            print("最小化窗口")

    def maximize_window(self) -> None:
        """最大化/还原窗口."""
        try:
            webview.windows[0].maximize()
        except AttributeError as e:
            print(f"最大化窗口失败: 未找到窗口: {e}")
        else:
            print("最大化窗口")

    def close_window(self) -> None:
        """关闭窗口."""
        try:
            webview.windows[0].destroy()
        except AttributeError as e:
            print(f"关闭窗口失败: {e}, 尝试退出应用...")
            sys.exit(0)
        else:
            print("关闭窗口")

    def get_system_info(self) -> dict:
        """获取系统信息.

        Returns:
            dict: 系统信息.
        """
        return {
            "platform": platform.system(),
            "architecture": platform.architecture()[0],
            "version": platform.version(),
            "python_version": platform.python_version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_path": sys.executable,
        }

    def get_app_version(self) -> str:
        """获取应用版本.

        Returns:
            str: 应用版本.
        """
        return "1.0.0"

    def get_cpu_usage(self) -> float:
        """获取CPU使用率.

        Returns:
            float: CPU使用率.
        """
        try:
            import psutil  # pyright: ignore[reportMissingModuleSource]

            return psutil.cpu_percent(interval=1)
        except ImportError:
            return 0.0

    def get_memory_info(self) -> dict:
        """获取内存信息.

        Returns:
            dict: 内存信息.
        """
        try:
            import psutil  # pyright: ignore[reportMissingModuleSource]
        except ImportError:
            return {"error": "psutil not installed"}
        else:
            memory = psutil.virtual_memory()
            return {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
            }

    def get_disk_info(self) -> dict:
        """获取磁盘信息.

        Returns:
            dict: 磁盘信息.
        """
        try:
            import psutil  # pyright: ignore[reportMissingModuleSource]

            disk = psutil.disk_usage("/")
            return {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100,
            }
        except ImportError:
            return {"error": "psutil not installed"}

    def open_file_dialog(
        self,
        _: Optional[tuple[str, ...]] = None,
    ) -> str:
        """打开文件对话框.

        Returns:
            str: 文件路径.
        """
        result = webview.windows[0].create_file_dialog(
            webview.FileDialog.OPEN,
            allow_multiple=False,
            file_types=("Text files (*.txt)", "Python files (*.py)"),
        )
        return result[0] if result else ""

    def save_file_dialog(
        self,
        default_path: str = "",
        _: Optional[tuple[Any, ...]] = None,
    ) -> Sequence[str] | None:
        """保存文件对话框.

        Args:
            default_path (str, optional): 默认保存路径. Defaults to "".

        Returns:
            Sequence[str]: 保存文件路径.
        """
        return webview.windows[0].create_file_dialog(
            webview.FileDialog.SAVE,
            file_types=("Image files (*.jpg;*.png;*.gif)", "All files (*.*)"),
            directory=default_path,
        )

    def open_url(self, url: str) -> bool:
        """在默认浏览器中打开URL.

        Returns:
            bool: 打开成功与否.
        """
        import webbrowser

        try:
            webbrowser.open(url)
        except Exception as e:  # noqa: BLE001
            print(f"打开URL失败: {e}")
            return False
        else:
            return True

    def get_clipboard_text(self) -> str:
        """获取剪贴板文本.

        Returns:
            str: 剪贴板文本.
        """
        try:
            import pyperclip  # pyright: ignore[reportMissingModuleSource]
        except ImportError:
            return ""
        else:
            return pyperclip.paste()

    def set_clipboard_text(self, text: str) -> bool:
        """设置剪贴板文本.

        Returns:
            bool: 设置成功与否.
        """
        try:
            import pyperclip  # pyright: ignore[reportMissingModuleSource]
        except ImportError:
            return False
        else:
            pyperclip.copy(text)
            return True
