"""服务层单元测试模块。"""

import time
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.services.rate_limiter import RateLimiter, login_rate_limiter
from app.services.token_blacklist import TokenBlacklist, token_blacklist
from app.utils.security import create_access_token, decode_access_token, get_password_hash, verify_password
from main import app
from app.models.database import Base, engine, SessionLocal
from app.models.user import User


@pytest.fixture(scope="function")
def client():
    """创建测试客户端。"""
    Base.metadata.create_all(bind=engine)
    login_rate_limiter._attempts.clear()
    login_rate_limiter._lockouts.clear()
    token_blacklist._blacklist.clear()

    with TestClient(app) as test_client:
        yield test_client

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


class TestRateLimiter:
    """速率限制器单元测试。"""

    def test_is_allowed_triggers_lockout(self):
        """测试is_allowed在达到最大尝试次数后触发锁定。"""
        limiter = RateLimiter(max_attempts=3, window_seconds=60, lockout_seconds=30)
        key = "test_key"

        # 手动记录3次失败尝试
        for _ in range(3):
            limiter.record_attempt(key, success=False)

        # 第4次检查应该被锁定
        allowed, wait_seconds = limiter.is_allowed(key)
        assert not allowed
        assert wait_seconds > 0

    def test_is_allowed_lockout_expires(self):
        """测试锁定过期后允许访问。"""
        # window_seconds也设为1秒，确保失败记录和锁定同时过期
        limiter = RateLimiter(max_attempts=2, window_seconds=1, lockout_seconds=1)
        key = "test_key"

        # 触发锁定
        limiter.record_attempt(key, success=False)
        limiter.record_attempt(key, success=False)
        allowed, _ = limiter.is_allowed(key)
        assert not allowed

        # 等待锁定和窗口期都过期
        time.sleep(1.1)

        # 锁定过期后应该允许
        allowed, wait_seconds = limiter.is_allowed(key)
        assert allowed
        assert wait_seconds == 0

    def test_check_and_record_lockout_expires(self):
        """测试check_and_record_attempt中锁定过期后清除。"""
        # window_seconds也设为1秒，确保失败记录和锁定同时过期
        limiter = RateLimiter(max_attempts=2, window_seconds=1, lockout_seconds=1)
        key = "test_key"

        # 触发锁定
        limiter.record_attempt(key, success=False)
        limiter.record_attempt(key, success=False)
        allowed, _, _ = limiter.check_and_record_attempt(key, success=False)
        assert not allowed

        # 等待锁定和窗口期都过期
        time.sleep(1.1)

        # 锁定过期后应该允许
        allowed, wait_seconds, remaining = limiter.check_and_record_attempt(key, success=True)
        assert allowed
        assert wait_seconds == 0

    def test_check_and_record_triggers_lockout(self):
        """测试check_and_record_attempt达到限制后触发锁定。"""
        limiter = RateLimiter(max_attempts=2, window_seconds=60, lockout_seconds=30)
        key = "test_key"

        # 第一次失败
        allowed, _, remaining = limiter.check_and_record_attempt(key, success=False)
        assert allowed
        assert remaining == 1

        # 第二次失败，触发锁定
        allowed, _, remaining = limiter.check_and_record_attempt(key, success=False)
        assert allowed  # 本次允许，但已记录
        assert remaining == 0

        # 第三次应该被锁定
        allowed, wait_seconds, _ = limiter.check_and_record_attempt(key, success=False)
        assert not allowed
        assert wait_seconds > 0

    def test_check_and_record_success_clears_lockout(self):
        """测试成功登录清除锁定状态。"""
        limiter = RateLimiter(max_attempts=3, window_seconds=60, lockout_seconds=30)
        key = "test_key"

        # 记录2次失败
        limiter.check_and_record_attempt(key, success=False)
        limiter.check_and_record_attempt(key, success=False)

        # 成功登录应该清除记录
        allowed, _, remaining = limiter.check_and_record_attempt(key, success=True)
        assert allowed
        assert remaining == 3  # 重置为最大值

        # 再次失败应该重新计数
        allowed, _, remaining = limiter.check_and_record_attempt(key, success=False)
        assert allowed
        assert remaining == 2

    def test_record_attempt_success_clears_all(self):
        """测试record_attempt成功时清除所有记录和锁定。"""
        limiter = RateLimiter(max_attempts=2, window_seconds=60, lockout_seconds=30)
        key = "test_key"

        # 记录失败尝试
        limiter.record_attempt(key, success=False)
        assert limiter.get_remaining_attempts(key) == 1

        # 成功尝试应该清除所有记录
        limiter.record_attempt(key, success=True)
        assert limiter.get_remaining_attempts(key) == 2

    def test_record_attempt_clears_lockout_on_success(self):
        """测试record_attempt成功时清除锁定。"""
        limiter = RateLimiter(max_attempts=2, window_seconds=60, lockout_seconds=30)
        key = "test_key"

        # 触发锁定
        limiter.record_attempt(key, success=False)
        limiter.record_attempt(key, success=False)
        allowed, _ = limiter.is_allowed(key)
        assert not allowed

        # 成功尝试应该清除锁定
        limiter.record_attempt(key, success=True)
        allowed, _ = limiter.is_allowed(key)
        assert allowed

    def test_window_expiry_clears_attempts(self):
        """测试窗口期过期后清除尝试记录。"""
        limiter = RateLimiter(max_attempts=3, window_seconds=1, lockout_seconds=30)
        key = "test_key"

        # 记录2次失败
        limiter.record_attempt(key, success=False)
        limiter.record_attempt(key, success=False)
        assert limiter.get_remaining_attempts(key) == 1

        # 等待窗口期过期
        time.sleep(1.1)

        # 窗口期过期后应该重置
        assert limiter.get_remaining_attempts(key) == 3


class TestTokenBlacklist:
    """令牌黑名单单元测试。"""

    def test_add_with_default_expiry(self):
        """测试添加令牌时使用默认过期时间。"""
        blacklist = TokenBlacklist()
        jti = "test_jti_default"

        # 不提供过期时间
        blacklist.add(jti)

        assert blacklist.is_blacklisted(jti)

    def test_add_with_custom_expiry(self):
        """测试添加令牌时使用自定义过期时间。"""
        blacklist = TokenBlacklist()
        jti = "test_jti_custom"
        exp = datetime.now(timezone.utc) + timedelta(hours=1)

        blacklist.add(jti, exp)

        assert blacklist.is_blacklisted(jti)

    def test_cleanup_removes_expired_entries(self):
        """测试清理过期的黑名单条目。"""
        blacklist = TokenBlacklist()
        jti_expired = "test_jti_expired"
        jti_valid = "test_jti_valid"

        # 添加一个已过期的条目
        expired_time = datetime.now(timezone.utc) - timedelta(seconds=1)
        blacklist._blacklist[jti_expired] = expired_time

        # 添加一个有效的条目（会触发清理）
        blacklist.add(jti_valid, datetime.now(timezone.utc) + timedelta(hours=1))

        # 过期条目应该被清理
        assert not blacklist.is_blacklisted(jti_expired)
        assert blacklist.is_blacklisted(jti_valid)

    def test_is_blacklisted_returns_false_for_unknown(self):
        """测试未知令牌返回False。"""
        blacklist = TokenBlacklist()
        assert not blacklist.is_blacklisted("unknown_jti")


class TestSecurity:
    """安全工具单元测试。"""

    def test_password_hash_and_verify(self):
        """测试密码哈希和验证。"""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)

    def test_create_access_token_with_default_expiry(self):
        """测试创建令牌使用默认过期时间。"""
        data = {"sub": "123"}
        token = create_access_token(data)

        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
        assert "exp" in payload
        assert "jti" in payload

    def test_create_access_token_with_custom_expiry(self):
        """测试创建令牌使用自定义过期时间。"""
        data = {"sub": "456"}
        expires_delta = timedelta(hours=2)
        token = create_access_token(data, expires_delta)

        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "456"

    def test_decode_invalid_token_returns_none(self):
        """测试解码无效令牌返回None。"""
        assert decode_access_token("invalid_token") is None

    def test_decode_expired_token_returns_none(self):
        """测试解码过期令牌返回None。"""
        data = {"sub": "789"}
        expires_delta = timedelta(seconds=-1)  # 已过期
        token = create_access_token(data, expires_delta)

        assert decode_access_token(token) is None


class TestDeps:
    """依赖注入模块测试。"""

    def test_get_current_user_optional_with_invalid_user_id(self, client, test_user_data):
        """测试令牌中user_id无效时返回None（触发ValueError）。"""
        from jose import jwt
        from app.config import settings

        # 创建一个sub为非数字的令牌
        token_data = {
            "sub": "not_a_number",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "jti": "test_jti"
        }
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        # 使用该令牌访问/me应该返回401
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401

    def test_get_current_user_optional_with_nonexistent_user(self, client, test_user_data):
        """测试令牌中user_id对应用户不存在时返回None。"""
        from jose import jwt
        from app.config import settings

        # 创建一个sub为不存在用户ID的令牌
        token_data = {
            "sub": "99999",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "jti": "test_jti_nonexistent"
        }
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        # 使用该令牌访问/me应该返回401
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401

    def test_get_current_user_optional_with_inactive_user(self, client, test_user_data):
        """测试令牌对应用户已禁用时返回None。"""
        from app.models.database import SessionLocal
        from app.models.user import User

        # 注册并登录获取令牌
        client.post("/api/auth/register", json=test_user_data)
        login_response = client.post("/api/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]

        # 禁用用户
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == test_user_data["username"]).first()
            user.is_active = False
            db.commit()
        finally:
            db.close()

        # 使用该令牌访问/me应该返回403（账户已被禁用）
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
        assert "禁用" in response.json()["detail"]

    def test_get_current_user_optional_with_no_sub(self, client):
        """测试令牌中没有sub字段时返回None。"""
        from jose import jwt
        from app.config import settings

        # 创建一个没有sub的令牌
        token_data = {
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "jti": "test_jti_no_sub"
        }
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        # 使用该令牌访问/me应该返回401
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
