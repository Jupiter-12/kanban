"""评论模型定义。"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from .database import Base, utc_now


class Comment(Base):
    """任务评论模型。"""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    # 关系
    task = relationship("Task", back_populates="comments")
    user = relationship("User", foreign_keys=[user_id], lazy="joined")
