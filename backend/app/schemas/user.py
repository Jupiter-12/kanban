"""用户相关的Pydantic模型。"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRoleEnum(str, Enum):
    """用户角色枚举。"""
    OWNER = "owner"  # 所有者（超级管理员）
    ADMIN = "admin"  # 管理员
    USER = "user"    # 普通用户


class UserBase(BaseModel):
    """用户基础模型。"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")


class UserCreate(UserBase):
    """用户注册请求模型。"""

    password: str = Field(..., min_length=6, max_length=100, description="密码")
    display_name: Optional[str] = Field(None, max_length=100, description="显示名称")


class UserLogin(BaseModel):
    """用户登录请求模型。"""

    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str  # 使用str而不是EmailStr，避免响应验证问题
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str = Field(default="user", description="用户角色")
    is_active: bool
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """令牌响应模型。"""

    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")


class TokenData(BaseModel):
    """令牌数据模型。"""

    user_id: Optional[int] = None


class UserListItem(BaseModel):
    """用户列表项模型（用于负责人选择）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: Optional[str] = None
    role: str = Field(default="user", description="用户角色")


class UserRoleUpdate(BaseModel):
    """用户角色更新请求模型。"""

    role: UserRoleEnum = Field(..., description="新角色")


class UserInfoUpdate(BaseModel):
    """用户信息更新请求模型（所有者用）。"""

    display_name: Optional[str] = Field(None, max_length=100, description="显示名称")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="新密码")
    is_active: Optional[bool] = Field(None, description="是否激活")


class UserSelfUpdate(BaseModel):
    """用户个人信息更新请求模型（用户自己用）。"""

    display_name: Optional[str] = Field(None, max_length=100, description="显示名称")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    current_password: Optional[str] = Field(None, description="当前密码（修改密码时必填）")
    new_password: Optional[str] = Field(None, min_length=6, max_length=100, description="新密码")
