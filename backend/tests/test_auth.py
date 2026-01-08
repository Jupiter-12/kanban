"""认证API测试模块。"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from main import app
from app.models.database import Base, engine, SessionLocal
from app.models.user import User
from app.services.rate_limiter import login_rate_limiter
from app.services.token_blacklist import token_blacklist


@pytest.fixture(scope="function")
def client():
    """创建测试客户端。"""
    # 创建测试数据库表
    Base.metadata.create_all(bind=engine)

    # 清理速率限制器和黑名单状态
    login_rate_limiter._attempts.clear()
    login_rate_limiter._lockouts.clear()
    token_blacklist._blacklist.clear()

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
def test_user_data():
    """测试用户数据。"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "display_name": "测试用户"
    }


class TestRegister:
    """用户注册测试。"""

    def test_register_success(self, client, test_user_data):
        """测试注册成功。"""
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["display_name"] == test_user_data["display_name"]
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_duplicate_username(self, client, test_user_data):
        """测试重复用户名注册。"""
        # 先注册一个用户
        client.post("/api/auth/register", json=test_user_data)

        # 尝试用相同用户名注册
        duplicate_data = test_user_data.copy()
        duplicate_data["email"] = "other@example.com"
        response = client.post("/api/auth/register", json=duplicate_data)
        assert response.status_code == 400
        assert "用户名已存在" in response.json()["detail"]

    def test_register_duplicate_email(self, client, test_user_data):
        """测试重复邮箱注册。"""
        # 先注册一个用户
        client.post("/api/auth/register", json=test_user_data)

        # 尝试用相同邮箱注册
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = "otheruser"
        response = client.post("/api/auth/register", json=duplicate_data)
        assert response.status_code == 400
        assert "邮箱已被注册" in response.json()["detail"]

    def test_register_invalid_email(self, client, test_user_data):
        """测试无效邮箱注册。"""
        test_user_data["email"] = "invalid-email"
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 422

    def test_register_short_password(self, client, test_user_data):
        """测试密码过短。"""
        test_user_data["password"] = "12345"
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 422

    def test_register_integrity_error_returns_400(self, client, monkeypatch, test_user_data):
        """测试数据库唯一性冲突时返回400而不是500。"""

        def raise_integrity_error(*_args, **_kwargs):
            raise IntegrityError("模拟唯一性冲突", params={}, orig=Exception("唯一性冲突"))

        monkeypatch.setattr("app.services.auth.AuthService.create_user", raise_integrity_error)

        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 400


class TestLogin:
    """用户登录测试。"""

    def test_login_success(self, client, test_user_data):
        """测试登录成功。"""
        # 先注册用户
        client.post("/api/auth/register", json=test_user_data)

        # 登录
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user_data):
        """测试密码错误。"""
        # 先注册用户
        client.post("/api/auth/register", json=test_user_data)

        # 用错误密码登录
        login_data = {
            "username": test_user_data["username"],
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
        assert "用户名或密码错误" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """测试不存在的用户登录。"""
        login_data = {
            "username": "nonexistent",
            "password": "somepassword"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401


class TestGetCurrentUser:
    """获取当前用户测试。"""

    def test_get_current_user_success(self, client, test_user_data):
        """测试获取当前用户成功。"""
        # 注册并登录
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]

        # 获取当前用户
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]

    def test_get_current_user_no_token(self, client):
        """测试无Token获取当前用户。"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """测试无效Token获取当前用户。"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


class TestLogout:
    """用户登出测试。"""

    def test_logout_without_token_returns_401(self, client):
        """测试无Token登出返回401。"""
        response = client.post("/api/auth/logout")
        assert response.status_code == 401
        assert "未认证" in response.json()["detail"]

    def test_logout_with_invalid_token_returns_401(self, client):
        """测试无效Token登出返回401。"""
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_logout_success(self, client, test_user_data):
        """测试有效Token登出成功。"""
        # 注册并登录
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]

        # 登出
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "登出成功"

    def test_logout_with_token_blacklist(self, client, test_user_data):
        """测试登出后令牌被加入黑名单。"""
        # 注册并登录
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]

        # 验证令牌有效
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        # 登出
        client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )

        # 验证令牌已失效
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401


class TestRateLimiting:
    """速率限制测试。"""

    def test_rate_limit_after_failed_attempts(self, client, test_user_data):
        """测试多次失败后触发速率限制。"""
        # 注册用户
        client.post("/api/auth/register", json=test_user_data)

        # 尝试5次错误密码
        for i in range(5):
            response = client.post("/api/auth/login", json={
                "username": test_user_data["username"],
                "password": "wrongpassword"
            })
            assert response.status_code == 401

        # 第6次应该被速率限制
        response = client.post("/api/auth/login", json={
            "username": test_user_data["username"],
            "password": "wrongpassword"
        })
        assert response.status_code == 429
        assert "登录尝试次数过多" in response.json()["detail"]

    def test_successful_login_resets_rate_limit(self, client, test_user_data):
        """测试成功登录后重置速率限制。"""
        # 注册用户
        client.post("/api/auth/register", json=test_user_data)

        # 尝试3次错误密码
        for i in range(3):
            client.post("/api/auth/login", json={
                "username": test_user_data["username"],
                "password": "wrongpassword"
            })

        # 成功登录
        response = client.post("/api/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        assert response.status_code == 200

        # 再次尝试错误密码，应该重新计数
        for i in range(4):
            response = client.post("/api/auth/login", json={
                "username": test_user_data["username"],
                "password": "wrongpassword"
            })
            assert response.status_code == 401  # 不应该是429

    def test_rate_limit_shows_remaining_attempts(self, client, test_user_data):
        """测试失败登录显示剩余尝试次数。"""
        # 注册用户
        client.post("/api/auth/register", json=test_user_data)

        # 第一次失败尝试
        response = client.post("/api/auth/login", json={
            "username": test_user_data["username"],
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        detail = response.json()["detail"]
        assert "剩余" in detail
        assert "次尝试机会" in detail

    def test_rate_limit_atomic_operation(self, client, test_user_data):
        """测试速率限制的原子操作（检查和记录同时进行）。"""
        # 注册用户
        client.post("/api/auth/register", json=test_user_data)

        # 连续5次失败尝试，每次都应该正确计数
        for i in range(5):
            response = client.post("/api/auth/login", json={
                "username": test_user_data["username"],
                "password": "wrongpassword"
            })
            assert response.status_code == 401
            if i < 4:  # 前4次应该显示剩余次数
                detail = response.json()["detail"]
                expected_remaining = 4 - i
                assert f"剩余{expected_remaining}次尝试机会" in detail

        # 第6次应该被锁定
        response = client.post("/api/auth/login", json={
            "username": test_user_data["username"],
            "password": "wrongpassword"
        })
        assert response.status_code == 429

    def test_disabled_user_login_records_failure(self, client, test_user_data):
        """测试禁用用户登录时也会记录失败尝试。"""
        # 注册用户
        client.post("/api/auth/register", json=test_user_data)

        # 禁用用户
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == test_user_data["username"]).first()
            user.is_active = False
            db.commit()
        finally:
            db.close()

        # 尝试登录禁用用户，应该返回403但也会记录失败
        response = client.post("/api/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        assert response.status_code == 403
        assert "用户已被禁用" in response.json()["detail"]

        # 验证失败记录被正确记录（通过检查速率限制器状态）
        client_ip = "testclient"
        rate_limit_key = f"{client_ip}:{test_user_data['username']}"
        remaining = login_rate_limiter.get_remaining_attempts(rate_limit_key)
        assert remaining == 4  # 应该减少了1次
