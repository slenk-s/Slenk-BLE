"""日志工具 — 文件 + 控制台双输出"""

import logging
import sys
from pathlib import Path


_LOG_DIR = Path.home() / ".ble-monitor" / "logs"


def setup_logger(name: str = "BLE-Monitor", level: int = logging.DEBUG) -> logging.Logger:
    """配置并返回命名 logger。

    - 控制台输出：INFO 及以上级别
    - 文件输出：DEBUG 及以上级别，完整格式
    """
    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    # 控制台 handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    ))

    # 文件 handler
    log_file = _LOG_DIR / "ble-monitor.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    ))

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger
