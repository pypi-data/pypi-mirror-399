import os
from enum import Enum
from typing import List

from pydantic.v1 import BaseSettings


class Environment(str, Enum):
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"
    TEST = "test"

def get_environment() -> Environment:
    match os.getenv("APP_ENV", "development").lower():
        case "prod" | "production":
            return Environment.PRODUCTION
        case "test":
            return Environment.TEST
        case _:
            return Environment.DEVELOPMENT

class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "MOSS"
    PROJECT_DESCRIPTION: str = ""
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT = get_environment()

    # API配置
    API_V1_STR: str = "/api/v1"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = os.getenv("PORT", 8000)
    WORKERS: int = 4

    # 日志配置
    LOG_DIR: str =os.getenv(
        "LOG_DIR",
        "logs"
    )
    LOG_LEVEL: str = os.getenv(
        "LOG_LEVEL",
        "INFO"
    )
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT",
        "json"
    ) # json or console

    # 安全配置
    ALLOWED_ORIGINS: List[str] = [
        "*",
    ]

    # 数据库配置
    SNOWFLAKE_DATACENTER_ID: int = os.getenv("SNOWFLAKE_DATACENTER_ID", 0)

    DATABASE_URI: str = os.getenv(
        "DATABASE_URI",
        "sqlite:///./instance/moss.db"  # 使用异步SQLite驱动
    )

    ASYNC_DATABASE_URI: str = os.getenv(
        "ASYNC_DATABASE_URI",
        "sqlite+aiosqlite:///./instance/moss.db"  # 使用异步SQLite驱动
    )
    DB_TABLE_PREFIX = os.getenv(
        "DB_TABLE_PREFIX",
        "mo_"
    )

    MINIO_ENDPOINT: str = os.getenv(
        "MINIO_ENDPOINT",
        "http://127.0.0.1:9000"
    )

    MINIO_SHARE_ENDPOINT: str = os.getenv(
        "MINIO_SHARE_ENDPOINT",
        "http://127.0.0.1:9000/minio"
    )

    MINIO_ACCESS_KEY: str = os.getenv(
        "MINIO_ACCESS_KEY",
        ""
    )

    MINIO_SECRET_KEY: str = os.getenv(
        "MINIO_SECRET_KEY",
        ""
    )

    MINIO_DEFAULT_BUCKET: str = os.getenv(
        "MINIO_DEFAULT_BUCKET",
        "mo"
    )

    STORAGE_TYPE: str = os.getenv(
        "STORAGE_TYPE",
        "local"
    )

    OPENDAL_SCHEME: str = os.getenv(
        "OPENDAL_SCHEME",
        "fs"
    )
    OPENDAL_FS_ROOT: str = os.getenv(
        "OPENDAL_FS_ROOT",
        "storage"
    )

    TEMP_DIR: str = os.getenv(
        "TEMP_DIR",
        "temp"
    )

    AUTH_SECRET_KEY: str = os.getenv(
        "AUTH_SECRET_KEY",
        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    )
    AUTH_SECRET_ALGORITHM: str = os.getenv(
        "AUTH_SECRET_ALGORITHM",
        "HS256"
    )
    AUTH_ACCESS_TOKEN_EXPIRE: int = os.getenv(
        "AUTH_ACCESS_TOKEN_EXPIRE",
        30
    )

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
