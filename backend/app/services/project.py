"""项目服务模块。"""

from datetime import time, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from ..models.project import Project
from ..models.column import KanbanColumn
from ..models.task import Task
from ..schemas.project import ProjectCreate, ProjectUpdate
from ..schemas.task import TaskFilter


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

    def get_project_with_filter(
        self, project_id: int, task_filter: Optional[TaskFilter] = None
    ) -> Optional[Project]:
        """根据ID获取项目，支持任务筛选。

        Args:
            project_id: 项目ID
            task_filter: 任务筛选条件

        Returns:
            项目对象（带筛选后的任务），如果不存在则返回None
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None

        # 如果没有筛选条件，直接返回
        if not task_filter or not any([
            task_filter.keyword,
            task_filter.assignee_id,
            task_filter.priority,
            task_filter.due_date_start,
            task_filter.due_date_end,
        ]):
            return project

        # 获取项目的所有列ID
        column_ids = [col.id for col in project.columns]

        # 构建筛选查询
        query = self.db.query(Task).filter(Task.column_id.in_(column_ids))

        if task_filter.keyword:
            # 不区分大小写的模糊匹配，转义 LIKE 通配符防止意外匹配
            escaped_keyword = (
                task_filter.keyword
                .replace("\\", "\\\\")
                .replace("%", "\\%")
                .replace("_", "\\_")
            )
            query = query.filter(Task.title.ilike(f"%{escaped_keyword}%", escape="\\"))

        if task_filter.assignee_id is not None:
            query = query.filter(Task.assignee_id == task_filter.assignee_id)

        if task_filter.priority:
            query = query.filter(Task.priority == task_filter.priority.value)

        if task_filter.due_date_start:
            query = query.filter(Task.due_date >= task_filter.due_date_start)

        if task_filter.due_date_end:
            due_date_end = task_filter.due_date_end
            if due_date_end.time() == time.min:
                # 仅传日期时，按次日零点前包含
                due_date_end = due_date_end + timedelta(days=1)
                query = query.filter(Task.due_date < due_date_end)
            else:
                query = query.filter(Task.due_date <= due_date_end)

        # 获取筛选后的任务ID
        filtered_task_ids = {task.id for task in query.all()}

        # 过滤每个列的任务
        for column in project.columns:
            column.tasks = [task for task in column.tasks if task.id in filtered_task_ids]

        return project

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

    def get_all_projects(self) -> List[Project]:
        """获取所有项目。

        Returns:
            项目列表
        """
        return (
            self.db.query(Project)
            .order_by(Project.created_at.desc())
            .all()
        )

    def get_all_projects_paginated(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[List[Project], int]:
        """获取所有项目（分页）。

        Args:
            page: 页码（从1开始）
            page_size: 每页数量

        Returns:
            (项目列表, 总数量)
        """
        query = self.db.query(Project)
        total = query.count()
        projects = (
            query.order_by(Project.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return projects, total

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
