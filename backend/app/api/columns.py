"""看板列API路由。"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..deps import get_current_user
from ..models.database import get_db
from ..models.user import User
from ..schemas.column import (
    ColumnCreate,
    ColumnReorder,
    ColumnResponse,
)
from ..schemas.column import ColumnUpdate
from ..services.column import ColumnService
from ..services.project import ProjectService

router = APIRouter(tags=["看板列"])


def get_column_service(db: Session = Depends(get_db)) -> ColumnService:
    """获取列服务实例。"""
    return ColumnService(db)


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    """获取项目服务实例。"""
    return ProjectService(db)


@router.post(
    "/projects/{project_id}/columns",
    response_model=ColumnResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_column(
    project_id: int,
    column_data: ColumnCreate,
    current_user: User = Depends(get_current_user),
    column_service: ColumnService = Depends(get_column_service),
    project_service: ProjectService = Depends(get_project_service),
) -> ColumnResponse:
    """在项目中创建列。

    Args:
        project_id: 项目ID
        column_data: 列创建数据
        current_user: 当前用户
        column_service: 列服务
        project_service: 项目服务

    Returns:
        创建的列信息

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

    column = column_service.create_column(column_data, project_id)
    return column


# 注意：reorder 路由必须在 {column_id} 路由之前，否则会被错误匹配
@router.put("/columns/reorder", response_model=List[ColumnResponse])
def reorder_columns(
    reorder_data: ColumnReorder,
    current_user: User = Depends(get_current_user),
    column_service: ColumnService = Depends(get_column_service),
    project_service: ProjectService = Depends(get_project_service),
) -> List[ColumnResponse]:
    """重新排序列。

    Args:
        reorder_data: 列排序数据
        current_user: 当前用户
        column_service: 列服务
        project_service: 项目服务

    Returns:
        更新后的列列表

    Raises:
        HTTPException: 如果列不存在或无权访问
    """
    if not reorder_data.column_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="列ID列表不能为空",
        )

    # 获取第一个列以确定项目
    first_column = column_service.get_column_by_id(reorder_data.column_ids[0])
    if not first_column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="列不存在",
        )

    project = project_service.get_project_by_id(first_column.project_id)
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此项目的列",
        )

    # 验证所有列是否属于同一项目
    for column_id in reorder_data.column_ids[1:]:
        column = column_service.get_column_by_id(column_id)
        if not column:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"列 {column_id} 不存在",
            )
        if column.project_id != first_column.project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="所有列必须属于同一项目",
            )

    columns = column_service.reorder_columns(first_column.project_id, reorder_data.column_ids)
    return columns


@router.put("/columns/{column_id}", response_model=ColumnResponse)
def update_column(
    column_id: int,
    column_data: ColumnUpdate,
    current_user: User = Depends(get_current_user),
    column_service: ColumnService = Depends(get_column_service),
    project_service: ProjectService = Depends(get_project_service),
) -> ColumnResponse:
    """更新列。

    Args:
        column_id: 列ID
        column_data: 列更新数据
        current_user: 当前用户
        column_service: 列服务
        project_service: 项目服务

    Returns:
        更新后的列信息

    Raises:
        HTTPException: 如果列不存在或无权访问
    """
    column = column_service.get_column_by_id(column_id)
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="列不存在",
        )

    project = project_service.get_project_by_id(column.project_id)
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此列",
        )

    updated_column = column_service.update_column(column_id, column_data)
    return updated_column


@router.delete("/columns/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_column(
    column_id: int,
    current_user: User = Depends(get_current_user),
    column_service: ColumnService = Depends(get_column_service),
    project_service: ProjectService = Depends(get_project_service),
) -> None:
    """删除列。

    Args:
        column_id: 列ID
        current_user: 当前用户
        column_service: 列服务
        project_service: 项目服务

    Raises:
        HTTPException: 如果列不存在或无权访问
    """
    column = column_service.get_column_by_id(column_id)
    if not column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="列不存在",
        )

    project = project_service.get_project_by_id(column.project_id)
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此列",
        )

    column_service.delete_column(column_id)
