"""用户API路由。"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..deps import get_current_user
from ..models.database import get_db
from ..models.user import User
from ..schemas.user import UserListItem

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
