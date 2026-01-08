"""项目服务模块。"""

from typing import List, Optional

from sqlalchemy.orm import Session

from ..models.project import Project
from ..models.column import KanbanColumn
from ..schemas.project import ProjectCreate, ProjectUpdate


# 默认列名称
DEFAULT_COLUMNS = ["待办", "进行中", "已完成"]


class ProjectService:
    """项目服务类。"""

    def __init__(self, db: Session):
        """初始化项目服务。

        Args:
            db: 数据库会话
        """
        self.db = db

    def create_project(self, project_data: ProjectCreate, owner_id: int) -> Project:
        """创建新项目。

        Args:
            project_data: 项目创建数据
            owner_id: 创建者ID

        Returns:
            创建的项目对象
        """
        db_project = Project(
            name=project_data.name,
            description=project_data.description,
            owner_id=owner_id,
        )
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)

        # 创建默认列
        for position, column_name in enumerate(DEFAULT_COLUMNS):
            db_column = KanbanColumn(
                name=column_name,
                project_id=db_project.id,
                position=position,
            )
            self.db.add(db_column)
        self.db.commit()
        self.db.refresh(db_project)

        return db_project

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """根据ID获取项目。

        Args:
            project_id: 项目ID

        Returns:
            项目对象，如果不存在则返回None
        """
        return self.db.query(Project).filter(Project.id == project_id).first()

    def get_projects_by_owner(self, owner_id: int) -> List[Project]:
        """获取用户的所有项目。

        Args:
            owner_id: 用户ID

        Returns:
            项目列表
        """
        return (
            self.db.query(Project)
            .filter(Project.owner_id == owner_id)
            .order_by(Project.created_at.desc())
            .all()
        )

    def get_projects_by_owner_paginated(
        self, owner_id: int, page: int = 1, page_size: int = 10
    ) -> tuple[List[Project], int]:
        """获取用户的项目（分页）。

        Args:
            owner_id: 用户ID
            page: 页码（从1开始）
            page_size: 每页数量

        Returns:
            (项目列表, 总数量)
        """
        query = self.db.query(Project).filter(Project.owner_id == owner_id)
        total = query.count()
        projects = (
            query.order_by(Project.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return projects, total

    def update_project(
        self, project_id: int, project_data: ProjectUpdate
    ) -> Optional[Project]:
        """更新项目。

        Args:
            project_id: 项目ID
            project_data: 项目更新数据

        Returns:
            更新后的项目对象，如果不存在则返回None
        """
        db_project = self.get_project_by_id(project_id)
        if not db_project:
            return None

        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)

        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def delete_project(self, project_id: int) -> bool:
        """删除项目。

        Args:
            project_id: 项目ID

        Returns:
            删除成功返回True，项目不存在返回False
        """
        db_project = self.get_project_by_id(project_id)
        if not db_project:
            return False

        self.db.delete(db_project)
        self.db.commit()
        return True
