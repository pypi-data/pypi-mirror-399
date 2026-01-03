import json
import sys
from datetime import datetime

import logging
import os
from pathlib import Path
from typing import List, Any

import structlog

from mop.conf import settings, Environment

if not os.path.exists(settings.LOG_DIR):
    os.makedirs(settings.LOG_DIR)


def get_log_file_path() -> Path:
    env_prefix = settings.ENVIRONMENT.value
    return Path(settings.LOG_DIR) / f"app-{env_prefix}-{datetime.now().strftime('%Y-%m-%d')}.log"


class JsonlFileHandler(logging.Handler):
    def __init__(self, file_path: Path):
        super().__init__()
        self.file_path = file_path

    def emit(self, record: logging.LogRecord) -> None:
        try:
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "filename": record.filename,
                "line": record.lineno,
                "environment": settings.ENVIRONMENT.value,
            }
            if hasattr(record, "extra"):
                log_entry.update(record.extra)
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            self.handleError(record)

    def close(self) -> None:
        super().close()


def get_structlog_processors(include_file_info: bool = True) -> List[Any]:
    processors = [
        structlog.stdlib.filter_by_level,
        # structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if include_file_info:
        processors.append(
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.MODULE,
                    structlog.processors.CallsiteParameter.PATHNAME,
                }
            )
        )

    processors.append(lambda _, __, event_dict: {**event_dict})

    return processors


def setup_logging():
    # 确保日志目录存在
    file_handler = JsonlFileHandler(get_log_file_path())
    file_handler.setLevel(settings.LOG_LEVEL)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)

    shared_processors = get_structlog_processors(
        include_file_info=settings.ENVIRONMENT not in [Environment.PRODUCTION, Environment.TEST])

    logging.basicConfig(
        format="%(message)s",
        level=settings.LOG_LEVEL,
        handlers=[file_handler, console_handler],
    )

    if settings.LOG_FORMAT == "console":
        structlog.configure(
            processors=[
                *shared_processors,
                structlog.dev.ConsoleRenderer(),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        structlog.configure(
            processors=[
                *shared_processors,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    # # 配置日志格式
    # formatter = logging.Formatter(
    #     "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    # )

    # # 文件处理器
    # file_handler = RotatingFileHandler(
    #     os.path.join(log_dir, "app.log"),
    #     maxBytes=10 * 1024 * 1024,  # 10MB
    #     backupCount=5
    # )
    # file_handler.setFormatter(formatter)
    # file_handler.setLevel(logging.INFO)
    #
    # # 控制台处理器
    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(formatter)
    # console_handler.setLevel(logging.DEBUG)
    #
    # # 配置根日志器
    # root_logger = logging.getLogger()
    # root_logger.setLevel(logging.INFO)
    # root_logger.addHandler(file_handler)
    # root_logger.addHandler(console_handler)

    # 设置其他库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


setup_logging()

logger = structlog.get_logger()
logger.info("logging_initialized", log_format=settings.LOG_FORMAT)