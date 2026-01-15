"""评论相关的Pydantic模型。"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CommentUserInfo(BaseModel):
    """评论者信息模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: Optional[str] = None


class CommentCreate(BaseModel):
    """评论创建请求模型。"""

    content: str = Field(..., min_length=1, description="评论内容")


class CommentResponse(BaseModel):
    """评论响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    user_id: int
    content: str
    created_at: datetime
    user: CommentUserInfo
