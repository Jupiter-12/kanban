"""项目API路由。"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..deps import get_current_user
from ..models.database import get_db
from ..models.user import User, UserRole
from ..schemas.project import (
    PaginatedResponse,
    ProjectCreate,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectUpdate,
)
from ..schemas.task import TaskFilter, TaskPriority
from ..services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["项目"])


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    """获取项目服务实例。"""
    return ProjectService(db)


def can_edit_project(user: User, project) -> bool:
    """检查用户是否有权限编辑项目。

    Args:
        user: 当前用户
        project: 项目对象

    Returns:
        是否有编辑权限
    """
    # 所有者和管理员可以编辑任意项目
    if user.role in [UserRole.OWNER.value, UserRole.ADMIN.value]:
        return True
    # 普通用户只能编辑自己创建的项目
    return project.owner_id == user.id


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """创建项目。

    Args:
        project_data: 项目创建数据
        current_user: 当前用户
        project_service: 项目服务

    Returns:
        创建的项目信息
    """
    project = project_service.create_project(project_data, current_user.id)
    return project


@router.get("", response_model=List[ProjectResponse])
def get_projects(
    page: Optional[int] = Query(None, ge=1, description="页码（从1开始）"),
    page_size: Optional[int] = Query(None, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
) -> List[ProjectResponse]:
    """获取所有项目。

    Args:
        page: 页码（可选，不传则返回全部）
        page_size: 每页数量（可选）
        current_user: 当前用户
        project_service: 项目服务

    Returns:
        项目列表
    """
    return project_service.get_all_projects()


@router.get("/paginated", response_model=PaginatedResponse[ProjectResponse])
def get_projects_paginated(
    page: int = Query(1, ge=1, description="页码（从1开始）"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
) -> PaginatedResponse[ProjectResponse]:
    """获取所有项目（分页）。

    Args:
        page: 页码
        page_size: 每页数量
        current_user: 当前用户
        project_service: 项目服务

    Returns:
        分页的项目列表
    """
    projects, total = project_service.get_all_projects_paginated(page, page_size)
    total_pages = (total + page_size - 1) // page_size
    return PaginatedResponse(
        items=projects,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(
    project_id: int,
    keyword: Optional[str] = Query(None, description="标题关键词（模糊匹配）"),
    assignee_id: Optional[int] = Query(None, description="负责人ID"),
    priority: Optional[TaskPriority] = Query(None, description="优先级"),
    due_date_start: Optional[datetime] = Query(None, description="截止日期起始"),
    due_date_end: Optional[datetime] = Query(None, description="截止日期结束"),
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectDetailResponse:
    """获取项目详情（包含列和任务）。

    支持任务筛选参数：
    - keyword: 标题关键词（不区分大小写）
    - assignee_id: 负责人ID
    - priority: 优先级（high/medium/low）
    - due_date_start: 截止日期起始
    - due_date_end: 截止日期结束

    Args:
        project_id: 项目ID
        keyword: 标题关键词
        assignee_id: 负责人ID
        priority: 优先级
        due_date_start: 截止日期起始
        due_date_end: 截止日期结束
        current_user: 当前用户
        project_service: 项目服务

    Returns:
        项目详情

    Raises:
        HTTPException: 如果项目不存在
    """
    # 构建筛选条件
    task_filter = TaskFilter(
        keyword=keyword,
        assignee_id=assignee_id,
        priority=priority,
        due_date_start=due_date_start,
        due_date_end=due_date_end,
    )

    project = project_service.get_project_with_filter(project_id, task_filter)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在",
        )
    # 所有用户都可以查看任意项目
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """更新项目。

    Args:
        project_id: 项目ID
        project_data: 项目更新数据
        current_user: 当前用户
        project_service: 项目服务

    Returns:
        更新后的项目信息

    Raises:
        HTTPException: 如果项目不存在或无权访问
    """
    project = project_service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在",
        )
    if not can_edit_project(current_user, project):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此项目",
        )

    updated_project = project_service.update_project(project_id, project_data)
    return updated_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
) -> None:
    """删除项目。

    Args:
        project_id: 项目ID
        current_user: 当前用户
        project_service: 项目服务

    Raises:
        HTTPException: 如果项目不存在或无权访问
    """
    project = project_service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在",
        )
    if not can_edit_project(current_user, project):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此项目",
        )

    project_service.delete_project(project_id)
