"""项目相关的Pydantic模型。"""

from datetime import datetime
from typing import Optional, List, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型。"""

    items: List[T]
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class ProjectBase(BaseModel):
    """项目基础模型。"""

    name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")


class ProjectCreate(ProjectBase):
    """项目创建请求模型。"""

    pass


class ProjectUpdate(BaseModel):
    """项目更新请求模型。"""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")


class ProjectResponse(ProjectBase):
    """项目响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime


class ProjectDetailResponse(ProjectResponse):
    """项目详情响应模型（包含列和任务）。"""

    columns: List["ColumnWithTasksResponse"] = []


# 前向引用，需要在文件末尾更新
from app.schemas.column import ColumnWithTasksResponse

ProjectDetailResponse.model_rebuild()
