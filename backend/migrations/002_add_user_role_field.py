"""迁移脚本：为用户表添加角色字段。

此脚本为users表添加以下字段：
- role: 用户角色（owner/admin/user）
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
        cursor.execute("PRAGMA table_info(users)")
        columns = {row[1] for row in cursor.fetchall()}

        # 添加role字段
        if "role" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL")
            print("已添加 role 字段")

            # 将第一个用户设置为所有者
            cursor.execute("SELECT id FROM users ORDER BY id LIMIT 1")
            first_user = cursor.fetchone()
            if first_user:
                cursor.execute("UPDATE users SET role = 'owner' WHERE id = ?", (first_user[0],))
                print(f"已将用户ID {first_user[0]} 设置为所有者")
        else:
            print("role 字段已存在，跳过")

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
