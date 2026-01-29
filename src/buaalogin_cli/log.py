"""日志配置模块：集中管理日志设置，供所有模块导入使用"""

import sys

from loguru import logger

from .constants import LOG_FILE

# 移除 loguru 默认的 stderr handler，稍后重新配置
logger.remove()

# 日志格式
LOG_FORMAT_CONSOLE = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level:<8}</level> | "
    "<cyan>[{extra[trigger]}]</cyan> "
    "<level>{message}</level>"
)

LOG_FORMAT_FILE = (
    "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | [{extra[trigger]:<8}] | "
    "{name}:{function}:{line} - {message}"
)

# 配置默认 trigger（防止 KeyError）
logger.configure(extra={"trigger": "unknown"})

# 文件输出：永远记录 DEBUG 级别（带轮转和压缩）
logger.add(
    LOG_FILE,
    format=LOG_FORMAT_FILE,
    level="DEBUG",  # 文件永远记录全量日志
    encoding="utf-8",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
)

# 控制台 handler ID，用于动态切换级别
_console_handler_id: int | None = None


def setup_console(verbose: bool = False) -> None:
    """配置输出级别

    Args:
        verbose: True 时输出 DEBUG 级别，否则输出 INFO 级别
    """
    global _console_handler_id

    # 移除旧的控制台 handler
    if _console_handler_id is not None:
        logger.remove(_console_handler_id)

    level = "DEBUG" if verbose else "INFO"
    _console_handler_id = logger.add(
        sys.stderr,
        format=LOG_FORMAT_CONSOLE,
        level=level,
        colorize=True,
    )


# 默认 INFO 级别控制台输出
setup_console(verbose=False)

__all__ = ["logger", "setup_console"]
