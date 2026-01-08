"""项目API路由。"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..deps import get_current_user
from ..models.database import get_db
from ..models.user import User
from ..schemas.project import (
    PaginatedResponse,
    ProjectCreate,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectUpdate,
)
from ..services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["项目"])


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    """获取项目服务实例。"""
    return ProjectService(db)


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
    """获取当前用户的所有项目。

    Args:
        page: 页码（可选，不传则返回全部）
        page_size: 每页数量（可选）
        current_user: 当前用户
        project_service: 项目服务

    Returns:
        项目列表
    """
    return project_service.get_projects_by_owner(current_user.id)


@router.get("/paginated", response_model=PaginatedResponse[ProjectResponse])
def get_projects_paginated(
    page: int = Query(1, ge=1, description="页码（从1开始）"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
) -> PaginatedResponse[ProjectResponse]:
    """获取当前用户的项目（分页）。

    Args:
        page: 页码
        page_size: 每页数量
        current_user: 当前用户
        project_service: 项目服务

    Returns:
        分页的项目列表
    """
    projects, total = project_service.get_projects_by_owner_paginated(
        current_user.id, page, page_size
    )
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
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectDetailResponse:
    """获取项目详情（包含列和任务）。

    Args:
        project_id: 项目ID
        current_user: 当前用户
        project_service: 项目服务

    Returns:
        项目详情

    Raises:
        HTTPException: 如果项目不存在或无权访问
    """
    project = project_service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在",
        )
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此项目",
        )
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
    if project.owner_id != current_user.id:
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
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此项目",
        )

    project_service.delete_project(project_id)
