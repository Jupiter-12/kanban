"""用户API测试模块。"""

import pytest
from fastapi.testclient import TestClient

from main import app
from app.models.database import Base, engine, SessionLocal
from app.models.user import User


@pytest.fixture(scope="function")
def client():
    """创建测试客户端。"""
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client

    # 清理测试数据
    db = SessionLocal()
    try:
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
        "display_name": "测试用户",
    }
    client.post("/api/auth/register", json=user_data)
    login_response = client.post("/api/auth/login", json={
        "username": user_data["username"],
        "password": user_data["password"],
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestGetUsers:
    """获取用户列表测试。"""

    def test_get_users_success(self, client, auth_headers):
        """测试获取用户列表成功。"""
        response = client.get("/api/users", headers=auth_headers)
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 1
        # 验证返回的用户包含当前用户
        usernames = [u["username"] for u in users]
        assert "testuser" in usernames

    def test_get_users_returns_user_list_item_format(self, client, auth_headers):
        """测试返回的用户列表格式正确。"""
        response = client.get("/api/users", headers=auth_headers)
        assert response.status_code == 200
        users = response.json()
        for user in users:
            assert "id" in user
            assert "username" in user
            assert "display_name" in user
            # 不应该包含敏感信息
            assert "password" not in user
            assert "email" not in user

    def test_get_users_includes_display_name(self, client, auth_headers):
        """测试返回的用户包含显示名称。"""
        response = client.get("/api/users", headers=auth_headers)
        assert response.status_code == 200
        users = response.json()
        test_user = next((u for u in users if u["username"] == "testuser"), None)
        assert test_user is not None
        assert test_user["display_name"] == "测试用户"

    def test_get_users_excludes_inactive(self, client, auth_headers):
        """测试不返回已禁用的用户。"""
        # 创建另一个用户
        other_user_data = {
            "username": "inactiveuser",
            "email": "inactive@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=other_user_data)

        # 禁用该用户
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == "inactiveuser").first()
            user.is_active = False
            db.commit()
        finally:
            db.close()

        # 获取用户列表
        response = client.get("/api/users", headers=auth_headers)
        assert response.status_code == 200
        users = response.json()
        usernames = [u["username"] for u in users]
        assert "inactiveuser" not in usernames

    def test_get_users_multiple_users(self, client, auth_headers):
        """测试返回多个用户。"""
        # 创建更多用户
        for i in range(3):
            user_data = {
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "password": "password123",
            }
            client.post("/api/auth/register", json=user_data)

        response = client.get("/api/users", headers=auth_headers)
        assert response.status_code == 200
        users = response.json()
        # 应该有4个用户（testuser + user0, user1, user2）
        assert len(users) == 4

    def test_get_users_unauthorized(self, client):
        """测试未认证时获取用户列表。"""
        response = client.get("/api/users")
        assert response.status_code == 401
