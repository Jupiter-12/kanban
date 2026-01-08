"""应用配置管理。"""

import os
import secrets
import warnings
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_secret_key() -> str:
    """获取SECRET_KEY，生产环境必须从环境变量设置。"""
    key = os.getenv("SECRET_KEY")
    if key:
        return key

    # 开发环境：生成随机密钥并警告
    env = os.getenv("ENV", "development")
    if env == "production":
        raise ValueError("生产环境必须设置SECRET_KEY环境变量！")

    warnings.warn(
        "未设置SECRET_KEY环境变量，使用随机生成的密钥。"
        "这仅适用于开发环境，每次重启服务后令牌将失效。",
        UserWarning,
        stacklevel=2,
    )
    return secrets.token_urlsafe(32)


class Settings(BaseSettings):
    """应用配置。"""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # 环境配置
    ENV: str = "development"
    DEBUG: bool = True

    # JWT配置
    SECRET_KEY: str = _get_secret_key()
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # 数据库配置
    DATABASE_URL: Optional[str] = None


settings = Settings()
