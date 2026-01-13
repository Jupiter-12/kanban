"""认证服务模块。"""

from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models.user import User, UserRole
from ..schemas.user import UserCreate
from ..utils.security import get_password_hash, verify_password


class AuthService:
    """认证服务类。"""

    def __init__(self, db: Session):
        """初始化认证服务。

        Args:
            db: 数据库会话
        """
        self.db = db

    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户。

        Args:
            username: 用户名

        Returns:
            用户对象，如果不存在则返回None
        """
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户。

        Args:
            email: 邮箱

        Returns:
            用户对象，如果不存在则返回None
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户。

        Args:
            user_id: 用户ID

        Returns:
            用户对象，如果不存在则返回None
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_data: UserCreate) -> User:
        """创建新用户。

        Args:
            user_data: 用户注册数据

        Returns:
            创建的用户对象
        """
        # 检查是否是系统中的第一个用户
        is_first_user = self.db.query(User).count() == 0

        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            display_name=user_data.display_name or user_data.username,
            role=UserRole.OWNER.value if is_first_user else UserRole.USER.value,
        )
        self.db.add(db_user)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ValueError("用户名或邮箱已存在") from exc
        self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户凭据。

        Args:
            username: 用户名
            password: 密码

        Returns:
            验证成功返回用户对象，失败返回None
        """
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
