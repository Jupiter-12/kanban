"""项目模型定义。"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base, utc_now


class Project(Base):
    """项目模型。"""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # 关系
    owner = relationship("User", backref="projects")
    columns = relationship(
        "KanbanColumn",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="KanbanColumn.position",
    )
