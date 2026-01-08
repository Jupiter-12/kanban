"""任务相关的Pydantic模型。"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    """任务基础模型。"""

    title: str = Field(..., min_length=1, max_length=200, description="任务标题")


class TaskCreate(TaskBase):
    """任务创建请求模型。"""

    pass


class TaskUpdate(BaseModel):
    """任务更新请求模型。"""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="任务标题")


class TaskMove(BaseModel):
    """任务移动请求模型。"""

    target_column_id: int = Field(..., description="目标列ID")
    position: int = Field(..., ge=0, description="目标位置")


class TaskResponse(TaskBase):
    """任务响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    column_id: int
    position: int
    created_at: datetime
    updated_at: datetime
