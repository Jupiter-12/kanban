"""评论API路由。"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..deps import get_current_user
from ..models.database import get_db
from ..models.user import User
from ..schemas.comment import CommentCreate, CommentResponse
from ..services.comment import CommentService
from ..services.task import TaskService

router = APIRouter(tags=["评论"])


def get_comment_service(db: Session = Depends(get_db)) -> CommentService:
    """获取评论服务实例。"""
    return CommentService(db)


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """获取任务服务实例。"""
    return TaskService(db)


@router.get(
    "/tasks/{task_id}/comments",
    response_model=List[CommentResponse],
)
def get_task_comments(
    task_id: int,
    current_user: User = Depends(get_current_user),
    comment_service: CommentService = Depends(get_comment_service),
    task_service: TaskService = Depends(get_task_service),
) -> List[CommentResponse]:
    """获取任务的评论列表。

    Args:
        task_id: 任务ID
        current_user: 当前用户
        comment_service: 评论服务
        task_service: 任务服务

    Returns:
        评论列表

    Raises:
        HTTPException: 如果任务不存在
    """
    task = task_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )

    return comment_service.get_comments_by_task(task_id)


@router.post(
    "/tasks/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    task_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    comment_service: CommentService = Depends(get_comment_service),
    task_service: TaskService = Depends(get_task_service),
) -> CommentResponse:
    """添加任务评论。

    Args:
        task_id: 任务ID
        comment_data: 评论创建数据
        current_user: 当前用户
        comment_service: 评论服务
        task_service: 任务服务

    Returns:
        创建的评论信息

    Raises:
        HTTPException: 如果任务不存在或评论内容为空
    """
    task = task_service.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )

    if not comment_data.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="评论内容不能为空",
        )

    return comment_service.create_comment(task_id, current_user.id, comment_data)


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    comment_service: CommentService = Depends(get_comment_service),
) -> None:
    """删除评论（仅自己的评论）。

    Args:
        comment_id: 评论ID
        current_user: 当前用户
        comment_service: 评论服务

    Raises:
        HTTPException: 如果评论不存在或无权删除
    """
    comment = comment_service.get_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在",
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除他人评论",
        )

    comment_service.delete_comment(comment_id)
