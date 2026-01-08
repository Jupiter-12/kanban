"""认证API路由。"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..config import settings
from ..deps import get_auth_service, get_current_user
from ..models.user import User
from ..schemas.user import Token, UserCreate, UserLogin, UserResponse
from ..services.auth import AuthService
from ..services.rate_limiter import login_rate_limiter
from ..services.token_blacklist import token_blacklist
from ..utils.security import create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer(auto_error=False)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """用户注册。

    Args:
        user_data: 用户注册数据
        auth_service: 认证服务

    Returns:
        创建的用户信息

    Raises:
        HTTPException: 如果用户名或邮箱已存在
    """
    # 检查用户名是否已存在
    if auth_service.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )

    # 检查邮箱是否已存在
    if auth_service.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册",
        )

    # 创建用户
    try:
        user = auth_service.create_user(user_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或邮箱已存在",
        )
    return user


@router.post("/login", response_model=Token)
def login(
    request: Request,
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """用户登录。

    Args:
        request: HTTP请求对象
        login_data: 登录凭据
        auth_service: 认证服务

    Returns:
        访问令牌

    Raises:
        HTTPException: 如果凭据无效或被速率限制
    """
    # 获取客户端IP作为速率限制键
    client_ip = request.client.host if request.client else "unknown"
    rate_limit_key = f"{client_ip}:{login_data.username}"

    # 先检查是否被锁定（使用原子操作避免竞态条件）
    is_allowed, wait_seconds = login_rate_limiter.is_allowed(rate_limit_key)
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"登录尝试次数过多，请在{wait_seconds}秒后重试",
        )

    # 验证用户凭据
    user = auth_service.authenticate_user(login_data.username, login_data.password)

    # 使用原子操作记录尝试结果（无论成功或失败）
    # 这样可以避免检查和记录之间的竞态条件
    allowed, wait_seconds, remaining = login_rate_limiter.check_and_record_attempt(
        rate_limit_key, success=(user is not None and user.is_active)
    )

    if not user:
        if wait_seconds > 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"登录尝试次数过多，请在{wait_seconds}秒后重试",
            )
        detail = "用户名或密码错误"
        if remaining > 0:
            detail += f"，剩余{remaining}次尝试机会"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """用户登出。

    将当前令牌加入黑名单，使其失效。
    需要有效的认证Token才能登出。

    Args:
        current_user: 当前认证用户（用于验证Token有效性）
        credentials: HTTP认证凭据

    Returns:
        登出成功消息
    """
    if credentials:
        token = credentials.credentials
        payload = decode_access_token(token)
        if payload:
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti:
                # 将令牌加入黑名单
                exp_datetime = None
                if exp:
                    exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
                token_blacklist.add(jti, exp_datetime)

    return {"message": "登出成功"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前用户信息。

    Args:
        current_user: 当前认证用户

    Returns:
        当前用户信息
    """
    return current_user
