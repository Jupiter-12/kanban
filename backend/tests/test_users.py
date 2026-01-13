"""用户API测试模块。"""

import pytest
from fastapi.testclient import TestClient

from main import app
from app.models.database import Base, engine, SessionLocal
from app.models.user import User, UserRole


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
    """创建认证用户并返回认证头（第一个用户自动成为所有者）。"""
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


class TestUserRole:
    """用户角色测试。"""

    def test_first_user_is_owner(self, client):
        """测试第一个注册的用户自动成为所有者。"""
        user_data = {
            "username": "firstuser",
            "email": "first@example.com",
            "password": "password123",
        }
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201
        assert response.json()["role"] == "owner"

    def test_second_user_is_normal_user(self, client):
        """测试第二个注册的用户是普通用户。"""
        # 注册第一个用户
        first_user = {
            "username": "firstuser",
            "email": "first@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=first_user)

        # 注册第二个用户
        second_user = {
            "username": "seconduser",
            "email": "second@example.com",
            "password": "password123",
        }
        response = client.post("/api/auth/register", json=second_user)
        assert response.status_code == 201
        assert response.json()["role"] == "user"


class TestUpdateUserRole:
    """更新用户角色测试。"""

    def test_owner_can_set_admin(self, client, auth_headers):
        """测试所有者可以将用户设置为管理员。"""
        # 创建另一个用户
        other_user = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=other_user)

        # 获取该用户ID
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == "otheruser").first()
            user_id = user.id
        finally:
            db.close()

        # 所有者将该用户设置为管理员
        response = client.put(
            f"/api/users/{user_id}/role",
            json={"role": "admin"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["role"] == "admin"

    def test_owner_can_demote_admin(self, client, auth_headers):
        """测试所有者可以将管理员降级为普通用户。"""
        # 创建另一个用户
        other_user = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=other_user)

        # 获取该用户ID并设置为管理员
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == "otheruser").first()
            user_id = user.id
            user.role = UserRole.ADMIN.value
            db.commit()
        finally:
            db.close()

        # 所有者将该用户降级为普通用户
        response = client.put(
            f"/api/users/{user_id}/role",
            json={"role": "user"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["role"] == "user"

    def test_admin_cannot_manage_roles(self, client, auth_headers):
        """测试管理员不能管理用户角色。"""
        # 创建另一个用户并设置为管理员
        other_user = {
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=other_user)

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
        admin_token = login_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 创建第三个用户
        third_user = {
            "username": "thirduser",
            "email": "third@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=third_user)

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == "thirduser").first()
            user_id = user.id
        finally:
            db.close()

        # 管理员尝试修改用户角色
        response = client.put(
            f"/api/users/{user_id}/role",
            json={"role": "admin"},
            headers=admin_headers,
        )
        assert response.status_code == 403
        assert "只有所有者可以管理用户角色" in response.json()["detail"]

    def test_cannot_set_user_as_owner(self, client, auth_headers):
        """测试不能将用户设置为所有者。"""
        # 创建另一个用户
        other_user = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=other_user)

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == "otheruser").first()
            user_id = user.id
        finally:
            db.close()

        # 尝试将用户设置为所有者
        response = client.put(
            f"/api/users/{user_id}/role",
            json={"role": "owner"},
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "不能将用户设置为所有者" in response.json()["detail"]

    def test_cannot_modify_own_role(self, client, auth_headers):
        """测试不能修改自己的角色。"""
        # 获取当前用户ID
        me_response = client.get("/api/auth/me", headers=auth_headers)
        user_id = me_response.json()["id"]

        # 尝试修改自己的角色
        response = client.put(
            f"/api/users/{user_id}/role",
            json={"role": "admin"},
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "不能修改自己的角色" in response.json()["detail"]

    def test_update_nonexistent_user_role(self, client, auth_headers):
        """测试更新不存在用户的角色。"""
        response = client.put(
            "/api/users/99999/role",
            json={"role": "admin"},
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert "用户不存在" in response.json()["detail"]


class TestGetAllUsers:
    """获取所有用户完整信息测试。"""

    def test_owner_can_get_all_users(self, client, auth_headers):
        """测试所有者可以获取所有用户完整信息。"""
        # 创建另一个用户
        other_user = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=other_user)

        response = client.get("/api/users/all", headers=auth_headers)
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 2
        # 验证返回完整信息（包含email）
        for user in users:
            assert "id" in user
            assert "username" in user
            assert "email" in user
            assert "role" in user
            assert "is_active" in user

    def test_admin_cannot_get_all_users(self, client, auth_headers):
        """测试管理员不能获取所有用户完整信息。"""
        # 创建管理员用户
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

        response = client.get("/api/users/all", headers=admin_headers)
        assert response.status_code == 403
        assert "只有所有者可以查看所有用户信息" in response.json()["detail"]

    def test_normal_user_cannot_get_all_users(self, client, auth_headers):
        """测试普通用户不能获取所有用户完整信息。"""
        # 创建普通用户
        normal_user = {
            "username": "normaluser",
            "email": "normal@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=normal_user)

        # 普通用户登录
        login_response = client.post("/api/auth/login", json={
            "username": "normaluser",
            "password": "password123",
        })
        normal_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

        response = client.get("/api/users/all", headers=normal_headers)
        assert response.status_code == 403


class TestGetMyProfile:
    """获取当前用户个人信息测试。"""

    def test_get_my_profile_success(self, client, auth_headers):
        """测试获取当前用户个人信息成功。"""
        response = client.get("/api/users/me/profile", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["display_name"] == "测试用户"
        assert data["role"] == "owner"

    def test_get_my_profile_unauthorized(self, client):
        """测试未认证时获取个人信息。"""
        response = client.get("/api/users/me/profile")
        assert response.status_code == 401


class TestUpdateMyProfile:
    """更新当前用户个人信息测试。"""

    def test_update_display_name(self, client, auth_headers):
        """测试更新显示名称。"""
        response = client.put(
            "/api/users/me/profile",
            json={"display_name": "新显示名称"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["display_name"] == "新显示名称"

    def test_update_email(self, client, auth_headers):
        """测试更新邮箱。"""
        response = client.put(
            "/api/users/me/profile",
            json={"email": "newemail@example.com"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["email"] == "newemail@example.com"

    def test_update_email_already_used(self, client, auth_headers):
        """测试更新邮箱为已被使用的邮箱。"""
        # 创建另一个用户
        other_user = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=other_user)

        # 尝试更新为已被使用的邮箱
        response = client.put(
            "/api/users/me/profile",
            json={"email": "other@example.com"},
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "邮箱已被其他用户使用" in response.json()["detail"]

    def test_update_password_success(self, client, auth_headers):
        """测试更新密码成功。"""
        response = client.put(
            "/api/users/me/profile",
            json={
                "current_password": "testpassword123",
                "new_password": "newpassword456",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200

        # 验证新密码可以登录
        login_response = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "newpassword456",
        })
        assert login_response.status_code == 200

    def test_update_password_wrong_current(self, client, auth_headers):
        """测试更新密码时当前密码错误。"""
        response = client.put(
            "/api/users/me/profile",
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword456",
            },
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "当前密码错误" in response.json()["detail"]

    def test_update_password_without_current(self, client, auth_headers):
        """测试更新密码时未提供当前密码。"""
        response = client.put(
            "/api/users/me/profile",
            json={"new_password": "newpassword456"},
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "修改密码需要提供当前密码" in response.json()["detail"]

    def test_update_multiple_fields(self, client, auth_headers):
        """测试同时更新多个字段。"""
        response = client.put(
            "/api/users/me/profile",
            json={
                "display_name": "新名称",
                "email": "new@example.com",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "新名称"
        assert data["email"] == "new@example.com"


class TestGetUserDetail:
    """获取用户详情测试。"""

    def test_owner_can_get_user_detail(self, client, auth_headers):
        """测试所有者可以获取用户详情。"""
        # 创建另一个用户
        other_user = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=other_user)

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == "otheruser").first()
            user_id = user.id
        finally:
            db.close()

        response = client.get(f"/api/users/{user_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "otheruser"
        assert data["email"] == "other@example.com"

    def test_admin_cannot_get_user_detail(self, client, auth_headers):
        """测试管理员不能获取用户详情。"""
        # 创建管理员用户
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
            admin_id = admin.id
        finally:
            db.close()

        # 管理员登录
        login_response = client.post("/api/auth/login", json={
            "username": "adminuser",
            "password": "password123",
        })
        admin_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

        # 获取所有者ID
        me_response = client.get("/api/auth/me", headers=auth_headers)
        owner_id = me_response.json()["id"]

        response = client.get(f"/api/users/{owner_id}", headers=admin_headers)
        assert response.status_code == 403
        assert "只有所有者可以查看用户详情" in response.json()["detail"]

    def test_get_nonexistent_user_detail(self, client, auth_headers):
        """测试获取不存在用户的详情。"""
        response = client.get("/api/users/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "用户不存在" in response.json()["detail"]


class TestUpdateUserInfo:
    """更新用户信息测试（所有者操作）。"""

    def test_owner_can_update_user_display_name(self, client, auth_headers):
        """测试所有者可以更新用户显示名称。"""
        # 创建另一个用户
        other_user = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=other_user)

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == "otheruser").first()
            user_id = user.id
        finally:
            db.close()

        response = client.put(
            f"/api/users/{user_id}",
            json={"display_name": "新显示名称"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["display_name"] == "新显示名称"

    def test_owner_can_update_user_email(self, client, auth_headers):
        """测试所有者可以更新用户邮箱。"""
        # 创建另一个用户
        other_user = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=other_user)

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == "otheruser").first()
            user_id = user.id
        finally:
            db.close()

        response = client.put(
            f"/api/users/{user_id}",
            json={"email": "newemail@example.com"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["email"] == "newemail@example.com"

    def test_owner_can_update_user_password(self, client, auth_headers):
        """测试所有者可以重置用户密码。"""
        # 创建另一个用户
        other_user = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=other_user)

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == "otheruser").first()
            user_id = user.id
        finally:
            db.close()

        response = client.put(
            f"/api/users/{user_id}",
            json={"password": "newpassword456"},
            headers=auth_headers,
        )
        assert response.status_code == 200

        # 验证新密码可以登录
        login_response = client.post("/api/auth/login", json={
            "username": "otheruser",
            "password": "newpassword456",
        })
        assert login_response.status_code == 200

    def test_owner_can_disable_user(self, client, auth_headers):
        """测试所有者可以禁用用户。"""
        # 创建另一个用户
        other_user = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=other_user)

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == "otheruser").first()
            user_id = user.id
        finally:
            db.close()

        response = client.put(
            f"/api/users/{user_id}",
            json={"is_active": False},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_owner_cannot_disable_self(self, client, auth_headers):
        """测试所有者不能禁用自己。"""
        me_response = client.get("/api/auth/me", headers=auth_headers)
        user_id = me_response.json()["id"]

        response = client.put(
            f"/api/users/{user_id}",
            json={"is_active": False},
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "不能禁用自己的账户" in response.json()["detail"]

    def test_update_user_email_already_used(self, client, auth_headers):
        """测试更新用户邮箱为已被使用的邮箱。"""
        # 创建两个用户
        user1 = {
            "username": "user1",
            "email": "user1@example.com",
            "password": "password123",
        }
        user2 = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=user1)
        client.post("/api/auth/register", json=user2)

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == "user1").first()
            user_id = user.id
        finally:
            db.close()

        # 尝试将user1的邮箱更新为user2的邮箱
        response = client.put(
            f"/api/users/{user_id}",
            json={"email": "user2@example.com"},
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "邮箱已被其他用户使用" in response.json()["detail"]

    def test_admin_cannot_update_user_info(self, client, auth_headers):
        """测试管理员不能更新用户信息。"""
        # 创建管理员用户
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

        # 获取所有者ID
        me_response = client.get("/api/auth/me", headers=auth_headers)
        owner_id = me_response.json()["id"]

        response = client.put(
            f"/api/users/{owner_id}",
            json={"display_name": "新名称"},
            headers=admin_headers,
        )
        assert response.status_code == 403
        assert "只有所有者可以更新用户信息" in response.json()["detail"]

    def test_update_nonexistent_user_info(self, client, auth_headers):
        """测试更新不存在用户的信息。"""
        response = client.put(
            "/api/users/99999",
            json={"display_name": "新名称"},
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert "用户不存在" in response.json()["detail"]


class TestCreateUser:
    """创建用户测试（所有者操作）。"""

    def test_owner_can_create_user(self, client, auth_headers):
        """测试所有者可以创建用户。"""
        new_user = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "display_name": "新用户",
        }
        response = client.post("/api/users", json=new_user, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["display_name"] == "新用户"
        assert data["role"] == "user"  # 新创建的用户是普通用户

    def test_owner_create_user_default_display_name(self, client, auth_headers):
        """测试创建用户时不提供显示名称则使用用户名。"""
        new_user = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        }
        response = client.post("/api/users", json=new_user, headers=auth_headers)
        assert response.status_code == 201
        assert response.json()["display_name"] == "newuser"

    def test_create_user_duplicate_username(self, client, auth_headers):
        """测试创建用户时用户名已存在。"""
        # 创建第一个用户
        user1 = {
            "username": "duplicateuser",
            "email": "user1@example.com",
            "password": "password123",
        }
        client.post("/api/users", json=user1, headers=auth_headers)

        # 尝试创建同名用户
        user2 = {
            "username": "duplicateuser",
            "email": "user2@example.com",
            "password": "password123",
        }
        response = client.post("/api/users", json=user2, headers=auth_headers)
        assert response.status_code == 400
        assert "用户名或邮箱已存在" in response.json()["detail"]

    def test_create_user_duplicate_email(self, client, auth_headers):
        """测试创建用户时邮箱已存在。"""
        # 创建第一个用户
        user1 = {
            "username": "user1",
            "email": "duplicate@example.com",
            "password": "password123",
        }
        client.post("/api/users", json=user1, headers=auth_headers)

        # 尝试创建同邮箱用户
        user2 = {
            "username": "user2",
            "email": "duplicate@example.com",
            "password": "password123",
        }
        response = client.post("/api/users", json=user2, headers=auth_headers)
        assert response.status_code == 400
        assert "用户名或邮箱已存在" in response.json()["detail"]

    def test_admin_cannot_create_user(self, client, auth_headers):
        """测试管理员不能创建用户。"""
        # 创建管理员用户
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

        new_user = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        }
        response = client.post("/api/users", json=new_user, headers=admin_headers)
        assert response.status_code == 403
        assert "只有所有者可以创建用户" in response.json()["detail"]


class TestDeleteUser:
    """删除用户测试（所有者操作）。"""

    def test_owner_can_delete_user(self, client, auth_headers):
        """测试所有者可以删除用户。"""
        # 创建另一个用户
        other_user = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=other_user)

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == "otheruser").first()
            user_id = user.id
        finally:
            db.close()

        response = client.delete(f"/api/users/{user_id}", headers=auth_headers)
        assert response.status_code == 204

        # 验证用户已删除
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            assert user is None
        finally:
            db.close()

    def test_owner_cannot_delete_self(self, client, auth_headers):
        """测试所有者不能删除自己。"""
        me_response = client.get("/api/auth/me", headers=auth_headers)
        user_id = me_response.json()["id"]

        response = client.delete(f"/api/users/{user_id}", headers=auth_headers)
        assert response.status_code == 400
        assert "不能删除自己的账户" in response.json()["detail"]

    def test_delete_nonexistent_user(self, client, auth_headers):
        """测试删除不存在的用户。"""
        response = client.delete("/api/users/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "用户不存在" in response.json()["detail"]

    def test_admin_cannot_delete_user(self, client, auth_headers):
        """测试管理员不能删除用户。"""
        # 创建管理员用户
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

        # 创建要删除的用户
        target_user = {
            "username": "targetuser",
            "email": "target@example.com",
            "password": "password123",
        }
        client.post("/api/auth/register", json=target_user)

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == "targetuser").first()
            user_id = user.id
        finally:
            db.close()

        response = client.delete(f"/api/users/{user_id}", headers=admin_headers)
        assert response.status_code == 403
        assert "只有所有者可以删除用户" in response.json()["detail"]
