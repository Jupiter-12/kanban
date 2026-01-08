"""看板列相关的Pydantic模型。"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class ColumnBase(BaseModel):
    """列基础模型。"""

    name: str = Field(..., min_length=1, max_length=100, description="列名称")


class ColumnCreate(ColumnBase):
    """列创建请求模型。"""

    pass


class ColumnUpdate(BaseModel):
    """列更新请求模型。"""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="列名称")


class ColumnReorder(BaseModel):
    """列排序请求模型。"""

    column_ids: List[int] = Field(..., description="按顺序排列的列ID列表")


class ColumnResponse(ColumnBase):
    """列响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    position: int
    created_at: datetime
    updated_at: datetime


class ColumnWithTasksResponse(ColumnResponse):
    """列响应模型（包含任务）。"""

    tasks: List["TaskResponse"] = []


# 前向引用，需要在文件末尾更新
from app.schemas.task import TaskResponse

ColumnWithTasksResponse.model_rebuild()
