"""评论服务模块。"""

from typing import List, Optional

from sqlalchemy.orm import Session

from ..models.comment import Comment
from ..schemas.comment import CommentCreate


class CommentService:
    """评论服务类。"""

    def __init__(self, db: Session):
        """初始化评论服务。

        Args:
            db: 数据库会话
        """
        self.db = db

    def create_comment(self, task_id: int, user_id: int, comment_data: CommentCreate) -> Comment:
        """创建评论。

        Args:
            task_id: 任务ID
            user_id: 用户ID
            comment_data: 评论创建数据

        Returns:
            创建的评论对象
        """
        db_comment = Comment(
            task_id=task_id,
            user_id=user_id,
            content=comment_data.content,
        )
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment

    def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        """根据ID获取评论。

        Args:
            comment_id: 评论ID

        Returns:
            评论对象，如果不存在则返回None
        """
        return self.db.query(Comment).filter(Comment.id == comment_id).first()

    def get_comments_by_task(self, task_id: int) -> List[Comment]:
        """获取任务的所有评论。

        Args:
            task_id: 任务ID

        Returns:
            评论列表，按时间倒序排列
        """
        return (
            self.db.query(Comment)
            .filter(Comment.task_id == task_id)
            .order_by(Comment.created_at.desc())
            .all()
        )

    def delete_comment(self, comment_id: int) -> bool:
        """删除评论。

        Args:
            comment_id: 评论ID

        Returns:
            删除成功返回True，评论不存在返回False
        """
        db_comment = self.get_comment_by_id(comment_id)
        if not db_comment:
            return False

        self.db.delete(db_comment)
        self.db.commit()
        return True
