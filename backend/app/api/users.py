"""用户API路由。"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from sqlalchemy.exc import IntegrityError

from ..deps import get_current_user
from ..models.database import get_db
from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserInfoUpdate, UserListItem, UserRoleUpdate, UserResponse, UserSelfUpdate
from ..utils.security import get_password_hash, verify_password

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("", response_model=List[UserListItem])
def get_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[User]:
    """获取所有用户列表（用于负责人选择）。

    Args:
        current_user: 当前用户（需要认证）
        db: 数据库会话

    Returns:
        用户列表
    """
    return db.query(User).filter(User.is_active.is_(True)).all()


@router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """更新用户角色（仅所有者可操作）。

    Args:
        user_id: 目标用户ID
        role_data: 角色更新数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        更新后的用户信息

    Raises:
        HTTPException: 如果无权操作或用户不存在
    """
    # 只有所有者可以管理用户角色
    if current_user.role != UserRole.OWNER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有所有者可以管理用户角色",
        )

    # 不能修改自己的角色
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的角色",
        )

    # 查找目标用户
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    # 不能将其他用户设置为所有者
    if role_data.role == UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能将用户设置为所有者",
        )

    # 更新角色
    target_user.role = role_data.role.value
    db.commit()
    db.refresh(target_user)
    return target_user


@router.get("/all", response_model=List[UserResponse])
def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[User]:
    """获取所有用户完整信息（仅所有者可操作）。

    Args:
        current_user: 当前用户
        db: 数据库会话

    Returns:
        用户列表

    Raises:
        HTTPException: 如果无权操作
    """
    # 只有所有者可以查看所有用户完整信息
    if current_user.role != UserRole.OWNER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有所有者可以查看所有用户信息",
        )

    return db.query(User).all()


@router.get("/me/profile", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前用户个人信息。

    Args:
        current_user: 当前用户

    Returns:
        当前用户信息
    """
    return current_user


@router.put("/me/profile", response_model=UserResponse)
def update_my_profile(
    user_data: UserSelfUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """更新当前用户个人信息。

    Args:
        user_data: 用户信息更新数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        更新后的用户信息

    Raises:
        HTTPException: 如果密码验证失败或邮箱已被使用
    """
    # 更新显示名称
    if user_data.display_name is not None:
        current_user.display_name = user_data.display_name

    # 更新邮箱
    if user_data.email is not None:
        # 检查邮箱是否已被其他用户使用
        existing_user = db.query(User).filter(
            User.email == user_data.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被其他用户使用",
            )
        current_user.email = user_data.email

    # 更新密码（需要验证当前密码）
    if user_data.new_password is not None:
        if user_data.current_password is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="修改密码需要提供当前密码",
            )
        if not verify_password(user_data.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当前密码错误",
            )
        current_user.password_hash = get_password_hash(user_data.new_password)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user_detail(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """获取用户详情（仅所有者可操作）。

    Args:
        user_id: 用户ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        用户详情

    Raises:
        HTTPException: 如果无权操作或用户不存在
    """
    # 只有所有者可以查看用户详情
    if current_user.role != UserRole.OWNER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有所有者可以查看用户详情",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user_info(
    user_id: int,
    user_data: UserInfoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """更新用户信息（仅所有者可操作）。

    Args:
        user_id: 目标用户ID
        user_data: 用户信息更新数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        更新后的用户信息

    Raises:
        HTTPException: 如果无权操作或用户不存在
    """
    # 只有所有者可以更新用户信息
    if current_user.role != UserRole.OWNER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有所有者可以更新用户信息",
        )

    # 查找目标用户
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    # 更新字段
    if user_data.display_name is not None:
        target_user.display_name = user_data.display_name
    if user_data.email is not None:
        # 检查邮箱是否已被其他用户使用
        existing_user = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被其他用户使用",
            )
        target_user.email = user_data.email
    if user_data.password is not None:
        target_user.password_hash = get_password_hash(user_data.password)
    if user_data.is_active is not None:
        # 不能禁用自己
        if user_id == current_user.id and not user_data.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能禁用自己的账户",
            )
        target_user.is_active = user_data.is_active

    db.commit()
    db.refresh(target_user)
    return target_user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """创建新用户（仅所有者可操作）。

    Args:
        user_data: 用户创建数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        创建的用户信息

    Raises:
        HTTPException: 如果无权操作或用户名/邮箱已存在
    """
    # 只有所有者可以创建用户
    if current_user.role != UserRole.OWNER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有所有者可以创建用户",
        )

    # 创建用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        display_name=user_data.display_name or user_data.username,
        role=UserRole.USER.value,
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或邮箱已存在",
        ) from exc
    db.refresh(new_user)
    return new_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """删除用户（仅所有者可操作）。

    Args:
        user_id: 目标用户ID
        current_user: 当前用户
        db: 数据库会话

    Raises:
        HTTPException: 如果无权操作、用户不存在或尝试删除自己
    """
    # 只有所有者可以删除用户
    if current_user.role != UserRole.OWNER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有所有者可以删除用户",
        )

    # 不能删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户",
        )

    # 查找目标用户
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    # 删除用户
    db.delete(target_user)
    db.commit()
