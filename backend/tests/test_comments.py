"""评论API测试模块。"""

import pytest
from fastapi.testclient import TestClient

from main import app
from app.models.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.column import KanbanColumn
from app.models.task import Task
from app.models.comment import Comment


@pytest.fixture(scope="function")
def client():
    """创建测试客户端。"""
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client

    # 清理测试数据
    db = SessionLocal()
    try:
        db.query(Comment).delete()
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


@pytest.fixture
def task_id(client, auth_headers):
    """创建测试项目和任务，返回任务ID。"""
    # 创建项目
    response = client.post(
        "/api/projects",
        json={"name": "测试项目"},
        headers=auth_headers,
    )
    project_id = response.json()["id"]

    # 获取默认列ID
    detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
    column_id = detail_response.json()["columns"][0]["id"]

    # 创建任务
    task_response = client.post(
        f"/api/columns/{column_id}/tasks",
        json={"title": "测试任务"},
        headers=auth_headers,
    )
    return task_response.json()["id"]


class TestCommentCreate:
    """评论创建测试。"""

    def test_create_comment_success(self, client, auth_headers, task_id):
        """测试创建评论成功。"""
        response = client.post(
            f"/api/tasks/{task_id}/comments",
            json={"content": "这是一条测试评论"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "这是一条测试评论"
        assert data["task_id"] == task_id
        assert "user" in data
        assert data["user"]["username"] == "testuser"

    def test_create_comment_multiline(self, client, auth_headers, task_id):
        """测试创建多行评论。"""
        content = "第一行\n第二行\n第三行"
        response = client.post(
            f"/api/tasks/{task_id}/comments",
            json={"content": content},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["content"] == content

    def test_create_comment_empty_content(self, client, auth_headers, task_id):
        """测试评论内容为空。"""
        response = client.post(
            f"/api/tasks/{task_id}/comments",
            json={"content": ""},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_comment_whitespace_only(self, client, auth_headers, task_id):
        """测试评论内容只有空白字符。"""
        response = client.post(
            f"/api/tasks/{task_id}/comments",
            json={"content": "   "},
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "不能为空" in response.json()["detail"]

    def test_create_comment_task_not_found(self, client, auth_headers):
        """测试在不存在的任务上创建评论。"""
        response = client.post(
            "/api/tasks/99999/comments",
            json={"content": "测试评论"},
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert "任务不存在" in response.json()["detail"]

    def test_create_comment_unauthorized(self, client, task_id):
        """测试未认证创建评论。"""
        response = client.post(
            f"/api/tasks/{task_id}/comments",
            json={"content": "测试评论"},
        )
        assert response.status_code == 401


class TestCommentList:
    """评论列表测试。"""

    def test_get_comments_empty(self, client, auth_headers, task_id):
        """测试获取空评论列表。"""
        response = client.get(
            f"/api/tasks/{task_id}/comments",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_get_comments_success(self, client, auth_headers, task_id):
        """测试获取评论列表成功。"""
        # 创建多条评论
        for i in range(3):
            client.post(
                f"/api/tasks/{task_id}/comments",
                json={"content": f"评论{i}"},
                headers=auth_headers,
            )

        response = client.get(
            f"/api/tasks/{task_id}/comments",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_comments_order_by_time_desc(self, client, auth_headers, task_id):
        """测试评论按时间倒序排列。"""
        # 创建多条评论
        client.post(
            f"/api/tasks/{task_id}/comments",
            json={"content": "第一条评论"},
            headers=auth_headers,
        )
        client.post(
            f"/api/tasks/{task_id}/comments",
            json={"content": "第二条评论"},
            headers=auth_headers,
        )
        client.post(
            f"/api/tasks/{task_id}/comments",
            json={"content": "第三条评论"},
            headers=auth_headers,
        )

        response = client.get(
            f"/api/tasks/{task_id}/comments",
            headers=auth_headers,
        )
        data = response.json()
        # 最新的评论应该在前面
        assert data[0]["content"] == "第三条评论"
        assert data[2]["content"] == "第一条评论"

    def test_get_comments_task_not_found(self, client, auth_headers):
        """测试获取不存在任务的评论。"""
        response = client.get(
            "/api/tasks/99999/comments",
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert "任务不存在" in response.json()["detail"]

    def test_get_comments_includes_user_info(self, client, auth_headers, task_id):
        """测试评论包含用户信息。"""
        client.post(
            f"/api/tasks/{task_id}/comments",
            json={"content": "测试评论"},
            headers=auth_headers,
        )

        response = client.get(
            f"/api/tasks/{task_id}/comments",
            headers=auth_headers,
        )
        data = response.json()
        assert len(data) == 1
        assert "user" in data[0]
        assert data[0]["user"]["username"] == "testuser"
        assert "id" in data[0]["user"]


class TestCommentDelete:
    """评论删除测试。"""

    def test_delete_own_comment_success(self, client, auth_headers, task_id):
        """测试删除自己的评论成功。"""
        # 创建评论
        create_response = client.post(
            f"/api/tasks/{task_id}/comments",
            json={"content": "待删除评论"},
            headers=auth_headers,
        )
        comment_id = create_response.json()["id"]

        # 删除评论
        response = client.delete(
            f"/api/comments/{comment_id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        # 验证评论已删除
        list_response = client.get(
            f"/api/tasks/{task_id}/comments",
            headers=auth_headers,
        )
        assert len(list_response.json()) == 0

    def test_delete_others_comment_forbidden(self, client, auth_headers, other_auth_headers, task_id):
        """测试删除他人评论被禁止。"""
        # 用户1创建评论
        create_response = client.post(
            f"/api/tasks/{task_id}/comments",
            json={"content": "用户1的评论"},
            headers=auth_headers,
        )
        comment_id = create_response.json()["id"]

        # 用户2尝试删除
        response = client.delete(
            f"/api/comments/{comment_id}",
            headers=other_auth_headers,
        )
        assert response.status_code == 403
        assert "无权删除" in response.json()["detail"]

    def test_delete_comment_not_found(self, client, auth_headers):
        """测试删除不存在的评论。"""
        response = client.delete(
            "/api/comments/99999",
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert "评论不存在" in response.json()["detail"]

    def test_delete_comment_unauthorized(self, client, auth_headers, task_id):
        """测试未认证删除评论。"""
        # 创建评论
        create_response = client.post(
            f"/api/tasks/{task_id}/comments",
            json={"content": "测试评论"},
            headers=auth_headers,
        )
        comment_id = create_response.json()["id"]

        # 未认证删除
        response = client.delete(f"/api/comments/{comment_id}")
        assert response.status_code == 401


class TestCommentCascadeDelete:
    """评论级联删除测试。"""

    def test_delete_task_cascades_comments(self, client, auth_headers, task_id):
        """测试删除任务时级联删除评论。"""
        # 创建评论
        client.post(
            f"/api/tasks/{task_id}/comments",
            json={"content": "评论1"},
            headers=auth_headers,
        )
        client.post(
            f"/api/tasks/{task_id}/comments",
            json={"content": "评论2"},
            headers=auth_headers,
        )

        # 删除任务
        client.delete(f"/api/tasks/{task_id}", headers=auth_headers)

        # 验证评论已被级联删除（通过数据库检查）
        db = SessionLocal()
        try:
            comments = db.query(Comment).filter(Comment.task_id == task_id).all()
            assert len(comments) == 0
        finally:
            db.close()
