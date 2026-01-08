"""任务模型定义。"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base, utc_now


class Task(Base):
    """任务卡片模型。"""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    column_id = Column(Integer, ForeignKey("columns.id"), nullable=False)
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # 关系
    column = relationship("KanbanColumn", back_populates="tasks")
