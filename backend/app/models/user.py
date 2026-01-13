"""用户模型定义。"""

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from .database import Base


def utc_now():
    """获取当前UTC时间。"""
    return datetime.now(timezone.utc)


class UserRole(str, Enum):
    """用户角色枚举。"""
    OWNER = "owner"  # 所有者（超级管理员）
    ADMIN = "admin"  # 管理员
    USER = "user"    # 普通用户


class User(Base):
    """用户模型。"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    role = Column(String(20), default=UserRole.USER.value, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
