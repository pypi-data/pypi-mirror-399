import logging
import shutil
from pathlib import Path

from fspacker.packers._base import BasePacker
from fspacker.settings import get_settings

logger = logging.getLogger(__name__)


class SourceResPacker(BasePacker):
    NAME = "源码 & 资源打包"

    def pack(self) -> None:
        if not self.info.normalized_dir:
            logger.error(f"项目文件夹不存在: {self.info.normalized_dir}")
            return

        if not self.info.source_file:
            logger.error(f"源文件不存在: {self.info.source_file}")
            return

        logger.debug(f"目标文件夹: [green bold]{self.info.dest_src_dir}")

        # 检查目标目录权限
        try:
            self.info.dest_src_dir.mkdir(parents=True, exist_ok=True)
            # 测试写入权限
            test_file = self.info.dest_src_dir / ".test_write"
            test_file.touch()
            test_file.unlink()
        except (PermissionError, OSError):
            logger.exception(
                f"无法创建或写入目标目录: {self.info.dest_src_dir}",
            )
            return

        source_folder = self.info.source_file.absolute().parent
        for entry in source_folder.iterdir():
            dest_path = self.info.dest_src_dir / entry.name

            if entry.is_file():
                if entry.name != "pyproject.toml":
                    logger.info(
                        f"复制目标文件: [green underline]{entry.name}[/]"
                        f" [bold green]:heavy_check_mark:",
                    )
                    shutil.copy2(entry, dest_path, follow_symlinks=False)
                else:
                    logger.info(f"跳过文件 [yellow]{entry.name}")
            elif entry.is_dir():
                if self.info.is_valid_entry(entry):
                    logger.info(
                        f"复制目标文件夹: [purple underline]{entry.name}[/]"
                        " [bold purple]:heavy_check_mark:",
                    )
                    # 使用统一的忽略函数避免复制不需要的子目录
                    shutil.copytree(
                        entry,
                        dest_path,
                        dirs_exist_ok=True,
                        ignore=self._ignore_patterns,
                        symlinks=False,
                    )
                else:
                    logger.info(f"跳过文件夹 [yellow]{entry.name}")

    def _ignore_patterns(self, directory: str, contents: list) -> set:
        """定义要忽略的模式.

        Returns:
            set: 忽略的目录
        """
        ignored: set[str] = set()
        # 忽略常见的不需要的目录
        ignore_dirs = get_settings().ignore_folders

        for item in contents:
            item_path = Path(directory) / item
            # 忽略指定目录和以特定模式开头的目录
            if (item_path.is_dir() and item in ignore_dirs) or (
                item_path.is_dir()
                and item.startswith((".", "__"))
                and item.endswith((".pyc", ".pyo", ".pyd"))
            ):
                ignored.add(item)

        return ignored
