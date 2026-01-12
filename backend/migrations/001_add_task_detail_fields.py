"""迁移脚本：为任务表添加详情字段。

此脚本为tasks表添加以下字段：
- description: 任务描述
- due_date: 截止日期
- priority: 优先级
- assignee_id: 负责人ID
"""

import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    """获取数据库文件路径。"""
    return Path(__file__).parent.parent.parent / "data" / "kanban.db"


def migrate():
    """执行迁移。"""
    db_path = get_db_path()

    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        print("将在应用启动时自动创建新表结构")
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(tasks)")
        columns = {row[1] for row in cursor.fetchall()}

        # 添加description字段
        if "description" not in columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN description TEXT")
            print("已添加 description 字段")

        # 添加due_date字段
        if "due_date" not in columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN due_date DATETIME")
            print("已添加 due_date 字段")

        # 添加priority字段
        if "priority" not in columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'medium' NOT NULL")
            print("已添加 priority 字段")

        # 添加assignee_id字段
        if "assignee_id" not in columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN assignee_id INTEGER REFERENCES users(id) ON DELETE SET NULL")
            print("已添加 assignee_id 字段")

        conn.commit()
        print("迁移完成")

    except Exception as e:
        conn.rollback()
        print(f"迁移失败: {e}")
        raise
    finally:
        conn.close()


def rollback():
    """回滚迁移（SQLite不支持删除列，仅作记录）。"""
    print("SQLite不支持删除列，回滚需要重建表")
    print("新字段均为可空，可以忽略不使用")


if __name__ == "__main__":
    migrate()
