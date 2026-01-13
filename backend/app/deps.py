"""FastAPI依赖注入模块。"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .models.database import get_db
from .models.user import User
from .services.auth import AuthService
from .services.token_blacklist import token_blacklist
from .utils.security import decode_access_token

# HTTP Bearer认证方案
security = HTTPBearer(auto_error=False)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """获取认证服务实例。

    Args:
        db: 数据库会话

    Returns:
        认证服务实例
    """
    return AuthService(db)


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[User]:
    """获取当前用户（可选）。

    Args:
        credentials: HTTP认证凭据
        auth_service: 认证服务

    Returns:
        当前用户对象，如果未认证则返回None

    Raises:
        HTTPException: 如果用户账户已被禁用
    """
    if not credentials:
        return None

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        return None

    # 检查令牌是否在黑名单中
    jti = payload.get("jti")
    if jti and token_blacklist.is_blacklisted(jti):
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    try:
        user_id = int(user_id)
    except ValueError:
        return None

    user = auth_service.get_user_by_id(user_id)
    if not user:
        return None

    # 用户被禁用时抛出明确的错误提示
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您的账户已被禁用，请联系管理员",
        )

    return user


def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional),
) -> User:
    """获取当前用户（必须认证）。

    Args:
        user: 当前用户

    Returns:
        当前用户对象

    Raises:
        HTTPException: 如果未认证或用户无效
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证或令牌无效",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
