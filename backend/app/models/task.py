"""任务模型定义。"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base, utc_now


class Task(Base):
    """任务卡片模型。"""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    priority = Column(String(10), nullable=False, default="medium")
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    column_id = Column(Integer, ForeignKey("columns.id"), nullable=False)
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # 关系
    column = relationship("KanbanColumn", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], lazy="joined")
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
