"""任务API路由。"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..deps import get_current_user
from ..models.database import get_db
from ..models.user import User, UserRole
from ..schemas.task import TaskCreate, TaskMove, TaskResponse, TaskUpdate
from ..services.column import ColumnService
from ..services.project import ProjectService
from ..services.task import TaskService

router = APIRouter(tags=["任务"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """获取任务服务实例。"""
    return TaskService(db)


def get_column_service(db: Session = Depends(get_db)) -> ColumnService:
    """获取列服务实例。"""
    return ColumnService(db)


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    """获取项目服务实例。"""
    return ProjectService(db)


def can_edit_project(user: User, project) -> bool:
    """检查用户是否有权限编辑项目。"""
    if user.role in [UserRole.OWNER.value, UserRole.ADMIN.value]:
        return True
    return project.owner_id == user.id


@router.post(
    "/columns/{column_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    column_id: int,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
    column_service: ColumnService = Depends(get_column_service),
    project_service: ProjectService = Depends(get_project_service),
) -> TaskResponse:
    """在列中创建任务。

    Args:
        column_id: 列ID
        task_data: 任务创建数据
        current_user: 当前用户
        task_service: 任务服务
        column_service: 列服务
        project_service: 项目服务

    Returns:
        创建的任务信息

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
    if not can_edit_project(current_user, project):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此列",
        )

    try:
        task = task_service.create_task(task_data, column_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
    column_service: ColumnService = Depends(get_column_service),
    project_service: ProjectService = Depends(get_project_service),
) -> TaskResponse:
    """更新任务。

    Args:
        task_id: 任务ID
        task_data: 任务更新数据
        current_user: 当前用户
        task_service: 任务服务
        column_service: 列服务
        project_service: 项目服务

    Returns:
        更新后的任务信息

    Raises:
        HTTPException: 如果任务不存在或无权访问
    """
    task = task_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )

    column = column_service.get_column_by_id(task.column_id)
    project = project_service.get_project_by_id(column.project_id)
    if not can_edit_project(current_user, project):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此任务",
        )

    try:
        updated_task = task_service.update_task(task_id, task_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return updated_task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
    column_service: ColumnService = Depends(get_column_service),
    project_service: ProjectService = Depends(get_project_service),
) -> None:
    """删除任务。

    Args:
        task_id: 任务ID
        current_user: 当前用户
        task_service: 任务服务
        column_service: 列服务
        project_service: 项目服务

    Raises:
        HTTPException: 如果任务不存在或无权访问
    """
    task = task_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )

    column = column_service.get_column_by_id(task.column_id)
    project = project_service.get_project_by_id(column.project_id)
    if not can_edit_project(current_user, project):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此任务",
        )

    task_service.delete_task(task_id)


@router.put("/tasks/{task_id}/move", response_model=TaskResponse)
def move_task(
    task_id: int,
    move_data: TaskMove,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
    column_service: ColumnService = Depends(get_column_service),
    project_service: ProjectService = Depends(get_project_service),
) -> TaskResponse:
    """移动任务到指定列的指定位置。

    Args:
        task_id: 任务ID
        move_data: 任务移动数据
        current_user: 当前用户
        task_service: 任务服务
        column_service: 列服务
        project_service: 项目服务

    Returns:
        移动后的任务信息

    Raises:
        HTTPException: 如果任务不存在或无权访问
    """
    task = task_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )

    # 验证源列权限
    source_column = column_service.get_column_by_id(task.column_id)
    source_project = project_service.get_project_by_id(source_column.project_id)
    if not can_edit_project(current_user, source_project):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权移动此任务",
        )

    # 验证目标列存在且属于同一项目
    target_column = column_service.get_column_by_id(move_data.target_column_id)
    if not target_column:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标列不存在",
        )
    if target_column.project_id != source_column.project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="目标列必须属于同一项目",
        )

    moved_task = task_service.move_task(task_id, move_data.target_column_id, move_data.position)
    return moved_task
