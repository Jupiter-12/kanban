"""任务相关的Pydantic模型。"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskPriority(str, Enum):
    """任务优先级枚举。"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AssigneeInfo(BaseModel):
    """负责人信息模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: Optional[str] = None


class TaskBase(BaseModel):
    """任务基础模型。"""

    title: str = Field(..., min_length=1, max_length=200, description="任务标题")


class TaskCreate(TaskBase):
    """任务创建请求模型。"""

    description: Optional[str] = Field(None, description="任务描述")
    due_date: Optional[datetime] = Field(None, description="截止日期")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="优先级")
    assignee_id: Optional[int] = Field(None, description="负责人ID")


class TaskUpdate(BaseModel):
    """任务更新请求模型。"""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    due_date: Optional[datetime] = Field(None, description="截止日期")
    priority: Optional[TaskPriority] = Field(None, description="优先级")
    assignee_id: Optional[int] = Field(None, description="负责人ID")


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
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: Optional[int] = None
    assignee: Optional[AssigneeInfo] = None
    created_at: datetime
    updated_at: datetime
