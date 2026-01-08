"""看板列API测试模块。"""

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
def project_id(client, auth_headers):
    """创建测试项目并返回ID。"""
    response = client.post(
        "/api/projects",
        json={"name": "测试项目"},
        headers=auth_headers,
    )
    return response.json()["id"]


class TestColumnCreate:
    """列创建测试。"""

    def test_create_column_success(self, client, auth_headers, project_id):
        """测试创建列成功。"""
        column_data = {"name": "新列"}
        response = client.post(
            f"/api/projects/{project_id}/columns",
            json=column_data,
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "新列"
        assert data["project_id"] == project_id
        assert data["position"] == 3  # 默认有3列，新列位置为3

    def test_create_column_empty_name(self, client, auth_headers, project_id):
        """测试列名称为空。"""
        column_data = {"name": ""}
        response = client.post(
            f"/api/projects/{project_id}/columns",
            json=column_data,
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_column_project_not_found(self, client, auth_headers):
        """测试在不存在的项目中创建列。"""
        column_data = {"name": "新列"}
        response = client.post(
            "/api/projects/99999/columns",
            json=column_data,
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestColumnUpdate:
    """列更新测试。"""

    def test_update_column_success(self, client, auth_headers, project_id):
        """测试更新列成功。"""
        # 获取默认列ID
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        column_id = detail_response.json()["columns"][0]["id"]

        # 更新列
        response = client.put(
            f"/api/columns/{column_id}",
            json={"name": "新名称"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "新名称"

    def test_update_column_not_found(self, client, auth_headers):
        """测试更新不存在的列。"""
        response = client.put(
            "/api/columns/99999",
            json={"name": "新名称"},
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestColumnDelete:
    """列删除测试。"""

    def test_delete_column_success(self, client, auth_headers, project_id):
        """测试删除列成功。"""
        # 获取默认列ID
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        column_id = detail_response.json()["columns"][0]["id"]

        # 删除列
        response = client.delete(f"/api/columns/{column_id}", headers=auth_headers)
        assert response.status_code == 204

        # 验证列已删除
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        assert len(detail_response.json()["columns"]) == 2

    def test_delete_column_updates_positions(self, client, auth_headers, project_id):
        """测试删除列后更新其他列的位置。"""
        # 获取默认列
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        columns = detail_response.json()["columns"]
        first_column_id = columns[0]["id"]

        # 删除第一列
        client.delete(f"/api/columns/{first_column_id}", headers=auth_headers)

        # 验证剩余列的位置已更新
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        columns = detail_response.json()["columns"]
        positions = [col["position"] for col in columns]
        assert positions == [0, 1]


class TestColumnReorder:
    """列排序测试。"""

    def test_reorder_columns_success(self, client, auth_headers, project_id):
        """测试列排序成功。"""
        # 获取默认列
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        columns = detail_response.json()["columns"]
        column_ids = [col["id"] for col in columns]

        # 反转顺序
        reversed_ids = list(reversed(column_ids))
        response = client.put(
            "/api/columns/reorder",
            json={"column_ids": reversed_ids},
            headers=auth_headers,
        )
        assert response.status_code == 200

        # 验证顺序已更新
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        columns = detail_response.json()["columns"]
        new_ids = [col["id"] for col in columns]
        assert new_ids == reversed_ids

    def test_reorder_columns_empty_list(self, client, auth_headers):
        """测试空列表排序。"""
        response = client.put(
            "/api/columns/reorder",
            json={"column_ids": []},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_reorder_columns_different_projects(self, client, auth_headers):
        """测试排序不同项目的列。"""
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

        # 尝试混合排序不同项目的列
        response = client.put(
            "/api/columns/reorder",
            json={"column_ids": [column1_id, column2_id]},
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "同一项目" in response.json()["detail"]

    def test_reorder_columns_nonexistent_column(self, client, auth_headers, project_id):
        """测试排序包含不存在的列。"""
        # 获取项目的列ID
        detail = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        column_id = detail.json()["columns"][0]["id"]

        # 尝试排序包含不存在的列
        response = client.put(
            "/api/columns/reorder",
            json={"column_ids": [column_id, 99999]},
            headers=auth_headers,
        )
        assert response.status_code == 404


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


class TestColumnPermission:
    """列权限测试。"""

    def test_create_column_forbidden(self, client, auth_headers, other_auth_headers):
        """测试在他人项目中创建列。"""
        # 用户1创建项目
        response = client.post(
            "/api/projects",
            json={"name": "用户1的项目"},
            headers=auth_headers,
        )
        project_id = response.json()["id"]

        # 用户2尝试在用户1的项目中创建列
        response = client.post(
            f"/api/projects/{project_id}/columns",
            json={"name": "新列"},
            headers=other_auth_headers,
        )
        assert response.status_code == 403
        assert "无权" in response.json()["detail"]

    def test_update_column_forbidden(self, client, auth_headers, other_auth_headers):
        """测试更新他人项目的列。"""
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

        # 用户2尝试更新
        response = client.put(
            f"/api/columns/{column_id}",
            json={"name": "新名称"},
            headers=other_auth_headers,
        )
        assert response.status_code == 403
        assert "无权" in response.json()["detail"]

    def test_delete_column_forbidden(self, client, auth_headers, other_auth_headers):
        """测试删除他人项目的列。"""
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

        # 用户2尝试删除
        response = client.delete(f"/api/columns/{column_id}", headers=other_auth_headers)
        assert response.status_code == 403
        assert "无权" in response.json()["detail"]

    def test_reorder_columns_forbidden(self, client, auth_headers, other_auth_headers):
        """测试排序他人项目的列。"""
        # 用户1创建项目
        response = client.post(
            "/api/projects",
            json={"name": "用户1的项目"},
            headers=auth_headers,
        )
        project_id = response.json()["id"]

        # 获取默认列ID
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        column_ids = [col["id"] for col in detail_response.json()["columns"]]

        # 用户2尝试排序
        response = client.put(
            "/api/columns/reorder",
            json={"column_ids": list(reversed(column_ids))},
            headers=other_auth_headers,
        )
        assert response.status_code == 403
        assert "无权" in response.json()["detail"]


class TestColumnCascadeDelete:
    """列级联删除测试。"""

    def test_delete_column_cascade_tasks(self, client, auth_headers, project_id):
        """测试删除列时级联删除任务。"""
        # 获取默认列ID
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        column_id = detail_response.json()["columns"][0]["id"]

        # 在列中创建多个任务
        for i in range(3):
            client.post(
                f"/api/columns/{column_id}/tasks",
                json={"title": f"任务{i}"},
                headers=auth_headers,
            )

        # 验证任务已创建
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        tasks = detail_response.json()["columns"][0]["tasks"]
        assert len(tasks) == 3

        # 删除列
        response = client.delete(f"/api/columns/{column_id}", headers=auth_headers)
        assert response.status_code == 204

        # 验证列和任务都已删除
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        columns = detail_response.json()["columns"]
        assert len(columns) == 2
        # 确保没有任务残留在其他列
        for col in columns:
            assert len(col["tasks"]) == 0
