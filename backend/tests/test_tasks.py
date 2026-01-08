"""任务API测试模块。"""

import pytest
from fastapi.testclient import TestClient

from main import app
from app.models.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.column import KanbanColumn
from app.models.task import Task


@pytest.fixture(scope="function")
def client():
    """创建测试客户端。"""
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client

    # 清理测试数据
    db = SessionLocal()
    try:
        db.query(Task).delete()
        db.query(KanbanColumn).delete()
        db.query(Project).delete()
        db.query(User).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def auth_headers(client):
    """创建认证用户并返回认证头。"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
    }
    client.post("/api/auth/register", json=user_data)
    login_response = client.post("/api/auth/login", json={
        "username": user_data["username"],
        "password": user_data["password"],
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def project_and_column(client, auth_headers):
    """创建测试项目并返回项目ID和列ID。"""
    response = client.post(
        "/api/projects",
        json={"name": "测试项目"},
        headers=auth_headers,
    )
    project_id = response.json()["id"]

    # 获取默认列ID
    detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
    column_id = detail_response.json()["columns"][0]["id"]

    return {"project_id": project_id, "column_id": column_id}


class TestTaskCreate:
    """任务创建测试。"""

    def test_create_task_success(self, client, auth_headers, project_and_column):
        """测试创建任务成功。"""
        column_id = project_and_column["column_id"]
        task_data = {"title": "测试任务"}
        response = client.post(
            f"/api/columns/{column_id}/tasks",
            json=task_data,
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "测试任务"
        assert data["column_id"] == column_id
        assert data["position"] == 0

    def test_create_task_position_increment(self, client, auth_headers, project_and_column):
        """测试创建多个任务时位置递增。"""
        column_id = project_and_column["column_id"]

        # 创建第一个任务
        response1 = client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "任务1"},
            headers=auth_headers,
        )
        assert response1.json()["position"] == 0

        # 创建第二个任务
        response2 = client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "任务2"},
            headers=auth_headers,
        )
        assert response2.json()["position"] == 1

    def test_create_task_empty_title(self, client, auth_headers, project_and_column):
        """测试任务标题为空。"""
        column_id = project_and_column["column_id"]
        task_data = {"title": ""}
        response = client.post(
            f"/api/columns/{column_id}/tasks",
            json=task_data,
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_task_column_not_found(self, client, auth_headers):
        """测试在不存在的列中创建任务。"""
        task_data = {"title": "测试任务"}
        response = client.post(
            "/api/columns/99999/tasks",
            json=task_data,
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestTaskUpdate:
    """任务更新测试。"""

    def test_update_task_success(self, client, auth_headers, project_and_column):
        """测试更新任务成功。"""
        column_id = project_and_column["column_id"]

        # 创建任务
        create_response = client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "原标题"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # 更新任务
        response = client.put(
            f"/api/tasks/{task_id}",
            json={"title": "新标题"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "新标题"

    def test_update_task_not_found(self, client, auth_headers):
        """测试更新不存在的任务。"""
        response = client.put(
            "/api/tasks/99999",
            json={"title": "新标题"},
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestTaskDelete:
    """任务删除测试。"""

    def test_delete_task_success(self, client, auth_headers, project_and_column):
        """测试删除任务成功。"""
        column_id = project_and_column["column_id"]
        project_id = project_and_column["project_id"]

        # 创建任务
        create_response = client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "待删除任务"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # 删除任务
        response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 204

        # 验证任务已删除
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        tasks = detail_response.json()["columns"][0]["tasks"]
        assert len(tasks) == 0

    def test_delete_task_updates_positions(self, client, auth_headers, project_and_column):
        """测试删除任务后更新其他任务的位置。"""
        column_id = project_and_column["column_id"]
        project_id = project_and_column["project_id"]

        # 创建三个任务
        response1 = client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "任务1"},
            headers=auth_headers,
        )
        task1_id = response1.json()["id"]

        client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "任务2"},
            headers=auth_headers,
        )

        client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "任务3"},
            headers=auth_headers,
        )

        # 删除第一个任务
        client.delete(f"/api/tasks/{task1_id}", headers=auth_headers)

        # 验证剩余任务的位置已更新
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        tasks = detail_response.json()["columns"][0]["tasks"]
        positions = [task["position"] for task in tasks]
        assert positions == [0, 1]

    def test_delete_task_not_found(self, client, auth_headers):
        """测试删除不存在的任务。"""
        response = client.delete("/api/tasks/99999", headers=auth_headers)
        assert response.status_code == 404


class TestTaskMove:
    """任务移动测试。"""

    def test_move_task_same_column(self, client, auth_headers, project_and_column):
        """测试在同一列内移动任务。"""
        column_id = project_and_column["column_id"]
        project_id = project_and_column["project_id"]

        # 创建三个任务
        response1 = client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "任务1"},
            headers=auth_headers,
        )
        task1_id = response1.json()["id"]

        client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "任务2"},
            headers=auth_headers,
        )

        client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "任务3"},
            headers=auth_headers,
        )

        # 将第一个任务移动到位置2
        response = client.put(
            f"/api/tasks/{task1_id}/move",
            json={"target_column_id": column_id, "position": 2},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["position"] == 2

        # 验证所有任务位置
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        tasks = detail_response.json()["columns"][0]["tasks"]
        titles = [task["title"] for task in tasks]
        assert titles == ["任务2", "任务3", "任务1"]

    def test_move_task_to_another_column(self, client, auth_headers, project_and_column):
        """测试将任务移动到另一列。"""
        project_id = project_and_column["project_id"]

        # 获取两个列的ID
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        columns = detail_response.json()["columns"]
        column1_id = columns[0]["id"]
        column2_id = columns[1]["id"]

        # 在第一列创建任务
        response = client.post(
            f"/api/columns/{column1_id}/tasks",
            json={"title": "移动的任务"},
            headers=auth_headers,
        )
        task_id = response.json()["id"]

        # 移动到第二列
        move_response = client.put(
            f"/api/tasks/{task_id}/move",
            json={"target_column_id": column2_id, "position": 0},
            headers=auth_headers,
        )
        assert move_response.status_code == 200
        assert move_response.json()["column_id"] == column2_id
        assert move_response.json()["position"] == 0

        # 验证任务已移动
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        columns = detail_response.json()["columns"]
        column1_tasks = columns[0]["tasks"]
        column2_tasks = columns[1]["tasks"]
        assert len(column1_tasks) == 0
        assert len(column2_tasks) == 1
        assert column2_tasks[0]["title"] == "移动的任务"

    def test_move_task_not_found(self, client, auth_headers, project_and_column):
        """测试移动不存在的任务。"""
        column_id = project_and_column["column_id"]
        response = client.put(
            "/api/tasks/99999/move",
            json={"target_column_id": column_id, "position": 0},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_move_task_target_column_not_found(self, client, auth_headers, project_and_column):
        """测试移动到不存在的列。"""
        column_id = project_and_column["column_id"]

        # 创建任务
        response = client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "测试任务"},
            headers=auth_headers,
        )
        task_id = response.json()["id"]

        # 移动到不存在的列
        move_response = client.put(
            f"/api/tasks/{task_id}/move",
            json={"target_column_id": 99999, "position": 0},
            headers=auth_headers,
        )
        assert move_response.status_code == 404

    def test_move_task_cross_project(self, client, auth_headers):
        """测试移动任务到不同项目的列（应该失败）。"""
        # 创建两个项目
        response1 = client.post(
            "/api/projects",
            json={"name": "项目1"},
            headers=auth_headers,
        )
        project1_id = response1.json()["id"]

        response2 = client.post(
            "/api/projects",
            json={"name": "项目2"},
            headers=auth_headers,
        )
        project2_id = response2.json()["id"]

        # 获取两个项目的列ID
        detail1 = client.get(f"/api/projects/{project1_id}", headers=auth_headers)
        detail2 = client.get(f"/api/projects/{project2_id}", headers=auth_headers)
        column1_id = detail1.json()["columns"][0]["id"]
        column2_id = detail2.json()["columns"][0]["id"]

        # 在项目1的列中创建任务
        response = client.post(
            f"/api/columns/{column1_id}/tasks",
            json={"title": "测试任务"},
            headers=auth_headers,
        )
        task_id = response.json()["id"]

        # 尝试移动到项目2的列
        move_response = client.put(
            f"/api/tasks/{task_id}/move",
            json={"target_column_id": column2_id, "position": 0},
            headers=auth_headers,
        )
        assert move_response.status_code == 400
        assert "同一项目" in move_response.json()["detail"]


@pytest.fixture
def other_auth_headers(client):
    """创建另一个认证用户并返回认证头。"""
    user_data = {
        "username": "otheruser",
        "email": "other@example.com",
        "password": "otherpassword123",
    }
    client.post("/api/auth/register", json=user_data)
    login_response = client.post("/api/auth/login", json={
        "username": user_data["username"],
        "password": user_data["password"],
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestTaskPermission:
    """任务权限测试。"""

    def test_create_task_forbidden(self, client, auth_headers, other_auth_headers):
        """测试在他人项目的列中创建任务。"""
        # 用户1创建项目
        response = client.post(
            "/api/projects",
            json={"name": "用户1的项目"},
            headers=auth_headers,
        )
        project_id = response.json()["id"]

        # 获取默认列ID
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        column_id = detail_response.json()["columns"][0]["id"]

        # 用户2尝试在用户1的列中创建任务
        response = client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "测试任务"},
            headers=other_auth_headers,
        )
        assert response.status_code == 403
        assert "无权" in response.json()["detail"]

    def test_update_task_forbidden(self, client, auth_headers, other_auth_headers):
        """测试更新他人项目的任务。"""
        # 用户1创建项目和任务
        response = client.post(
            "/api/projects",
            json={"name": "用户1的项目"},
            headers=auth_headers,
        )
        project_id = response.json()["id"]

        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        column_id = detail_response.json()["columns"][0]["id"]

        task_response = client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "测试任务"},
            headers=auth_headers,
        )
        task_id = task_response.json()["id"]

        # 用户2尝试更新
        response = client.put(
            f"/api/tasks/{task_id}",
            json={"title": "新标题"},
            headers=other_auth_headers,
        )
        assert response.status_code == 403
        assert "无权" in response.json()["detail"]

    def test_delete_task_forbidden(self, client, auth_headers, other_auth_headers):
        """测试删除他人项目的任务。"""
        # 用户1创建项目和任务
        response = client.post(
            "/api/projects",
            json={"name": "用户1的项目"},
            headers=auth_headers,
        )
        project_id = response.json()["id"]

        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        column_id = detail_response.json()["columns"][0]["id"]

        task_response = client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "测试任务"},
            headers=auth_headers,
        )
        task_id = task_response.json()["id"]

        # 用户2尝试删除
        response = client.delete(f"/api/tasks/{task_id}", headers=other_auth_headers)
        assert response.status_code == 403
        assert "无权" in response.json()["detail"]

    def test_move_task_forbidden(self, client, auth_headers, other_auth_headers):
        """测试移动他人项目的任务。"""
        # 用户1创建项目和任务
        response = client.post(
            "/api/projects",
            json={"name": "用户1的项目"},
            headers=auth_headers,
        )
        project_id = response.json()["id"]

        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        columns = detail_response.json()["columns"]
        column1_id = columns[0]["id"]
        column2_id = columns[1]["id"]

        task_response = client.post(
            f"/api/columns/{column1_id}/tasks",
            json={"title": "测试任务"},
            headers=auth_headers,
        )
        task_id = task_response.json()["id"]

        # 用户2尝试移动
        response = client.put(
            f"/api/tasks/{task_id}/move",
            json={"target_column_id": column2_id, "position": 0},
            headers=other_auth_headers,
        )
        assert response.status_code == 403
        assert "无权" in response.json()["detail"]
