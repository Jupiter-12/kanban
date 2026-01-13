"""项目API测试模块。"""

import pytest
from fastapi.testclient import TestClient

from main import app
from app.models.database import Base, engine, SessionLocal
from app.models.user import User, UserRole
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


class TestProjectCreate:
    """项目创建测试。"""

    def test_create_project_success(self, client, auth_headers):
        """测试创建项目成功。"""
        project_data = {"name": "测试项目", "description": "这是一个测试项目"}
        response = client.post("/api/projects", json=project_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == project_data["name"]
        assert data["description"] == project_data["description"]
        assert "id" in data
        assert "owner_id" in data

    def test_create_project_with_default_columns(self, client, auth_headers):
        """测试创建项目时自动创建默认列。"""
        project_data = {"name": "测试项目"}
        response = client.post("/api/projects", json=project_data, headers=auth_headers)
        assert response.status_code == 201
        project_id = response.json()["id"]

        # 获取项目详情，检查默认列
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        assert detail_response.status_code == 200
        data = detail_response.json()
        assert len(data["columns"]) == 3
        column_names = [col["name"] for col in data["columns"]]
        assert "待办" in column_names
        assert "进行中" in column_names
        assert "已完成" in column_names

    def test_create_project_empty_name(self, client, auth_headers):
        """测试项目名称为空。"""
        project_data = {"name": ""}
        response = client.post("/api/projects", json=project_data, headers=auth_headers)
        assert response.status_code == 422

    def test_create_project_unauthorized(self, client):
        """测试未认证创建项目。"""
        project_data = {"name": "测试项目"}
        response = client.post("/api/projects", json=project_data)
        assert response.status_code == 401


class TestProjectList:
    """项目列表测试。"""

    def test_get_projects_empty(self, client, auth_headers):
        """测试获取空项目列表。"""
        response = client.get("/api/projects", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_get_projects_success(self, client, auth_headers):
        """测试获取项目列表成功。"""
        # 创建两个项目
        client.post("/api/projects", json={"name": "项目1"}, headers=auth_headers)
        client.post("/api/projects", json={"name": "项目2"}, headers=auth_headers)

        response = client.get("/api/projects", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_all_projects_visible(self, client, auth_headers, other_auth_headers):
        """测试所有用户可以查看所有项目。"""
        # 用户1创建项目
        client.post("/api/projects", json={"name": "用户1的项目"}, headers=auth_headers)
        # 用户2创建项目
        client.post("/api/projects", json={"name": "用户2的项目"}, headers=other_auth_headers)

        # 用户1可以看到所有项目
        response = client.get("/api/projects", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [p["name"] for p in data]
        assert "用户1的项目" in names
        assert "用户2的项目" in names

        # 用户2也可以看到所有项目
        response = client.get("/api/projects", headers=other_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestProjectDetail:
    """项目详情测试。"""

    def test_get_project_detail_success(self, client, auth_headers):
        """测试获取项目详情成功。"""
        # 创建项目
        create_response = client.post(
            "/api/projects",
            json={"name": "测试项目", "description": "描述"},
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "测试项目"
        assert data["description"] == "描述"
        assert "columns" in data

    def test_get_project_not_found(self, client, auth_headers):
        """测试获取不存在的项目。"""
        response = client.get("/api/projects/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "项目不存在" in response.json()["detail"]

    def test_get_other_user_project_allowed(self, client, auth_headers, other_auth_headers):
        """测试可以查看他人项目。"""
        # 用户1创建项目
        create_response = client.post(
            "/api/projects",
            json={"name": "用户1的项目"},
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        # 用户2可以查看
        response = client.get(f"/api/projects/{project_id}", headers=other_auth_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "用户1的项目"


class TestProjectPaginated:
    """项目分页测试。"""

    def test_get_projects_paginated_success(self, client, auth_headers):
        """测试分页获取项目成功。"""
        # 创建5个项目
        for i in range(5):
            client.post("/api/projects", json={"name": f"项目{i}"}, headers=auth_headers)

        # 获取第一页（每页2个）
        response = client.get(
            "/api/projects/paginated?page=1&page_size=2",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total_pages"] == 3

    def test_get_projects_paginated_last_page(self, client, auth_headers):
        """测试获取最后一页。"""
        # 创建5个项目
        for i in range(5):
            client.post("/api/projects", json={"name": f"项目{i}"}, headers=auth_headers)

        # 获取最后一页
        response = client.get(
            "/api/projects/paginated?page=3&page_size=2",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["page"] == 3

    def test_get_projects_paginated_empty(self, client, auth_headers):
        """测试分页获取空项目列表。"""
        response = client.get(
            "/api/projects/paginated?page=1&page_size=10",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0
        assert data["total"] == 0
        assert data["total_pages"] == 0


class TestProjectUpdate:
    """项目更新测试。"""

    def test_update_project_success(self, client, auth_headers):
        """测试更新项目成功。"""
        # 创建项目
        create_response = client.post(
            "/api/projects",
            json={"name": "原名称"},
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        # 更新项目
        response = client.put(
            f"/api/projects/{project_id}",
            json={"name": "新名称", "description": "新描述"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "新名称"
        assert data["description"] == "新描述"

    def test_update_project_partial(self, client, auth_headers):
        """测试部分更新项目。"""
        # 创建项目
        create_response = client.post(
            "/api/projects",
            json={"name": "原名称", "description": "原描述"},
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        # 只更新名称
        response = client.put(
            f"/api/projects/{project_id}",
            json={"name": "新名称"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "新名称"
        assert data["description"] == "原描述"

    def test_update_project_not_found(self, client, auth_headers):
        """测试更新不存在的项目。"""
        response = client.put(
            "/api/projects/99999",
            json={"name": "新名称"},
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert "项目不存在" in response.json()["detail"]

    def test_update_project_forbidden(self, client, auth_headers, other_auth_headers):
        """测试更新他人项目。"""
        # 用户1创建项目
        create_response = client.post(
            "/api/projects",
            json={"name": "用户1的项目"},
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        # 用户2尝试更新
        response = client.put(
            f"/api/projects/{project_id}",
            json={"name": "新名称"},
            headers=other_auth_headers,
        )
        assert response.status_code == 403
        assert "无权修改" in response.json()["detail"]


class TestProjectDelete:
    """项目删除测试。"""

    def test_delete_project_success(self, client, auth_headers):
        """测试删除项目成功。"""
        # 创建项目
        create_response = client.post(
            "/api/projects",
            json={"name": "待删除项目"},
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        # 删除项目
        response = client.delete(f"/api/projects/{project_id}", headers=auth_headers)
        assert response.status_code == 204

        # 验证项目已删除
        get_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_project_not_found(self, client, auth_headers):
        """测试删除不存在的项目。"""
        response = client.delete("/api/projects/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "项目不存在" in response.json()["detail"]

    def test_delete_project_forbidden(self, client, auth_headers, other_auth_headers):
        """测试删除他人项目。"""
        # 用户1创建项目
        create_response = client.post(
            "/api/projects",
            json={"name": "用户1的项目"},
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        # 用户2尝试删除
        response = client.delete(f"/api/projects/{project_id}", headers=other_auth_headers)
        assert response.status_code == 403
        assert "无权删除" in response.json()["detail"]

    def test_delete_project_cascade(self, client, auth_headers):
        """测试删除项目级联删除列和任务。"""
        # 创建项目
        create_response = client.post(
            "/api/projects",
            json={"name": "待删除项目"},
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        # 获取默认列ID
        detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        column_id = detail_response.json()["columns"][0]["id"]

        # 在列中创建任务
        client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "测试任务"},
            headers=auth_headers,
        )

        # 删除项目
        response = client.delete(f"/api/projects/{project_id}", headers=auth_headers)
        assert response.status_code == 204

        # 验证项目已删除
        get_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        assert get_response.status_code == 404


class TestProjectRolePermissions:
    """项目角色权限测试。"""

    def test_owner_can_edit_any_project(self, client, auth_headers, other_auth_headers):
        """测试所有者可以编辑任意项目。"""
        # 用户2创建项目（用户1是所有者）
        create_response = client.post(
            "/api/projects",
            json={"name": "用户2的项目"},
            headers=other_auth_headers,
        )
        project_id = create_response.json()["id"]

        # 用户1（所有者）可以编辑
        response = client.put(
            f"/api/projects/{project_id}",
            json={"name": "所有者修改的名称"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "所有者修改的名称"

    def test_admin_can_edit_any_project(self, client, auth_headers, other_auth_headers):
        """测试管理员可以编辑任意项目。"""
        # 创建第三个用户并设置为管理员
        admin_user = {
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=admin_user)

        db = SessionLocal()
        try:
            admin = db.query(User).filter(User.username == "adminuser").first()
            admin.role = UserRole.ADMIN.value
            db.commit()
        finally:
            db.close()

        # 管理员登录
        login_response = client.post("/api/auth/login", json={
            "username": "adminuser",
            "password": "password123",
        })
        admin_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

        # 用户2创建项目
        create_response = client.post(
            "/api/projects",
            json={"name": "用户2的项目"},
            headers=other_auth_headers,
        )
        project_id = create_response.json()["id"]

        # 管理员可以编辑
        response = client.put(
            f"/api/projects/{project_id}",
            json={"name": "管理员修改的名称"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "管理员修改的名称"

    def test_normal_user_cannot_edit_others_project(self, client, auth_headers, other_auth_headers):
        """测试普通用户不能编辑他人项目。"""
        # 用户1创建项目（用户1是所有者，用户2是普通用户）
        create_response = client.post(
            "/api/projects",
            json={"name": "用户1的项目"},
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        # 用户2（普通用户）不能编辑
        response = client.put(
            f"/api/projects/{project_id}",
            json={"name": "用户2尝试修改"},
            headers=other_auth_headers,
        )
        assert response.status_code == 403
        assert "无权修改" in response.json()["detail"]

    def test_normal_user_can_edit_own_project(self, client, auth_headers, other_auth_headers):
        """测试普通用户可以编辑自己的项目。"""
        # 用户2创建项目
        create_response = client.post(
            "/api/projects",
            json={"name": "用户2的项目"},
            headers=other_auth_headers,
        )
        project_id = create_response.json()["id"]

        # 用户2可以编辑自己的项目
        response = client.put(
            f"/api/projects/{project_id}",
            json={"name": "用户2修改的名称"},
            headers=other_auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "用户2修改的名称"

    def test_owner_can_delete_any_project(self, client, auth_headers, other_auth_headers):
        """测试所有者可以删除任意项目。"""
        # 用户2创建项目
        create_response = client.post(
            "/api/projects",
            json={"name": "用户2的项目"},
            headers=other_auth_headers,
        )
        project_id = create_response.json()["id"]

        # 用户1（所有者）可以删除
        response = client.delete(f"/api/projects/{project_id}", headers=auth_headers)
        assert response.status_code == 204

    def test_normal_user_cannot_delete_others_project(self, client, auth_headers, other_auth_headers):
        """测试普通用户不能删除他人项目。"""
        # 用户1创建项目
        create_response = client.post(
            "/api/projects",
            json={"name": "用户1的项目"},
            headers=auth_headers,
        )
        project_id = create_response.json()["id"]

        # 用户2（普通用户）不能删除
        response = client.delete(f"/api/projects/{project_id}", headers=other_auth_headers)
        assert response.status_code == 403
        assert "无权删除" in response.json()["detail"]
