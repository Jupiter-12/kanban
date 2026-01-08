"""看板列服务模块。"""

from typing import List, Optional

from sqlalchemy.orm import Session

from ..models.column import KanbanColumn
from ..schemas.column import ColumnCreate, ColumnUpdate


class ColumnService:
    """看板列服务类。"""

    def __init__(self, db: Session):
        """初始化列服务。

        Args:
            db: 数据库会话
        """
        self.db = db

    def create_column(self, column_data: ColumnCreate, project_id: int) -> KanbanColumn:
        """创建新列。

        Args:
            column_data: 列创建数据
            project_id: 项目ID

        Returns:
            创建的列对象
        """
        # 获取当前项目的最大位置
        max_position = (
            self.db.query(KanbanColumn)
            .filter(KanbanColumn.project_id == project_id)
            .count()
        )

        db_column = KanbanColumn(
            name=column_data.name,
            project_id=project_id,
            position=max_position,
        )
        self.db.add(db_column)
        self.db.commit()
        self.db.refresh(db_column)
        return db_column

    def get_column_by_id(self, column_id: int) -> Optional[KanbanColumn]:
        """根据ID获取列。

        Args:
            column_id: 列ID

        Returns:
            列对象，如果不存在则返回None
        """
        return self.db.query(KanbanColumn).filter(KanbanColumn.id == column_id).first()

    def get_columns_by_project(self, project_id: int) -> List[KanbanColumn]:
        """获取项目的所有列。

        Args:
            project_id: 项目ID

        Returns:
            列列表
        """
        return (
            self.db.query(KanbanColumn)
            .filter(KanbanColumn.project_id == project_id)
            .order_by(KanbanColumn.position)
            .all()
        )

    def update_column(
        self, column_id: int, column_data: ColumnUpdate
    ) -> Optional[KanbanColumn]:
        """更新列。

        Args:
            column_id: 列ID
            column_data: 列更新数据

        Returns:
            更新后的列对象，如果不存在则返回None
        """
        db_column = self.get_column_by_id(column_id)
        if not db_column:
            return None

        update_data = column_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_column, field, value)

        self.db.commit()
        self.db.refresh(db_column)
        return db_column

    def delete_column(self, column_id: int) -> bool:
        """删除列。

        Args:
            column_id: 列ID

        Returns:
            删除成功返回True，列不存在返回False
        """
        db_column = self.get_column_by_id(column_id)
        if not db_column:
            return False

        project_id = db_column.project_id
        position = db_column.position

        self.db.delete(db_column)

        # 更新后续列的位置
        self.db.query(KanbanColumn).filter(
            KanbanColumn.project_id == project_id,
            KanbanColumn.position > position,
        ).update({KanbanColumn.position: KanbanColumn.position - 1})

        self.db.commit()
        return True

    def reorder_columns(self, project_id: int, column_ids: List[int]) -> List[KanbanColumn]:
        """重新排序列。

        Args:
            project_id: 项目ID
            column_ids: 按顺序排列的列ID列表

        Returns:
            更新后的列列表
        """
        for position, column_id in enumerate(column_ids):
            self.db.query(KanbanColumn).filter(
                KanbanColumn.id == column_id,
                KanbanColumn.project_id == project_id,
            ).update({KanbanColumn.position: position})

        self.db.commit()
        return self.get_columns_by_project(project_id)
