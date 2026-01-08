"""任务服务模块。"""

from typing import List, Optional

from sqlalchemy.orm import Session

from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """任务服务类。"""

    def __init__(self, db: Session):
        """初始化任务服务。

        Args:
            db: 数据库会话
        """
        self.db = db

    def create_task(self, task_data: TaskCreate, column_id: int) -> Task:
        """创建新任务。

        Args:
            task_data: 任务创建数据
            column_id: 列ID

        Returns:
            创建的任务对象
        """
        # 获取当前列的最大位置
        max_position = (
            self.db.query(Task)
            .filter(Task.column_id == column_id)
            .count()
        )

        db_task = Task(
            title=task_data.title,
            column_id=column_id,
            position=max_position,
        )
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """根据ID获取任务。

        Args:
            task_id: 任务ID

        Returns:
            任务对象，如果不存在则返回None
        """
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_tasks_by_column(self, column_id: int) -> List[Task]:
        """获取列的所有任务。

        Args:
            column_id: 列ID

        Returns:
            任务列表
        """
        return (
            self.db.query(Task)
            .filter(Task.column_id == column_id)
            .order_by(Task.position)
            .all()
        )

    def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """更新任务。

        Args:
            task_id: 任务ID
            task_data: 任务更新数据

        Returns:
            更新后的任务对象，如果不存在则返回None
        """
        db_task = self.get_task_by_id(task_id)
        if not db_task:
            return None

        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)

        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def delete_task(self, task_id: int) -> bool:
        """删除任务。

        Args:
            task_id: 任务ID

        Returns:
            删除成功返回True，任务不存在返回False
        """
        db_task = self.get_task_by_id(task_id)
        if not db_task:
            return False

        column_id = db_task.column_id
        position = db_task.position

        self.db.delete(db_task)

        # 更新后续任务的位置
        self.db.query(Task).filter(
            Task.column_id == column_id,
            Task.position > position,
        ).update({Task.position: Task.position - 1})

        self.db.commit()
        return True

    def move_task(self, task_id: int, target_column_id: int, position: int) -> Optional[Task]:
        """移动任务到指定列的指定位置。

        Args:
            task_id: 任务ID
            target_column_id: 目标列ID
            position: 目标位置

        Returns:
            移动后的任务对象，如果任务不存在则返回None
        """
        db_task = self.get_task_by_id(task_id)
        if not db_task:
            return None

        source_column_id = db_task.column_id
        source_position = db_task.position

        # 如果是同一列内移动
        if source_column_id == target_column_id:
            if source_position < position:
                # 向下移动：中间的任务位置减1
                self.db.query(Task).filter(
                    Task.column_id == source_column_id,
                    Task.position > source_position,
                    Task.position <= position,
                ).update({Task.position: Task.position - 1})
            elif source_position > position:
                # 向上移动：中间的任务位置加1
                self.db.query(Task).filter(
                    Task.column_id == source_column_id,
                    Task.position >= position,
                    Task.position < source_position,
                ).update({Task.position: Task.position + 1})
        else:
            # 跨列移动
            # 源列：后续任务位置减1
            self.db.query(Task).filter(
                Task.column_id == source_column_id,
                Task.position > source_position,
            ).update({Task.position: Task.position - 1})

            # 目标列：目标位置及之后的任务位置加1
            self.db.query(Task).filter(
                Task.column_id == target_column_id,
                Task.position >= position,
            ).update({Task.position: Task.position + 1})

            db_task.column_id = target_column_id

        db_task.position = position
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
