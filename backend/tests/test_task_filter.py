"""任务筛选API测试模块。"""

import pytest
from datetime import datetime, timedelta
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
def project_with_tasks(client, auth_headers):
    """创建带有多个任务的项目用于筛选测试。"""
    # 创建项目
    response = client.post(
        "/api/projects",
        json={"name": "筛选测试项目"},
        headers=auth_headers,
    )
    project_id = response.json()["id"]

    # 获取默认列ID
    detail_response = client.get(f"/api/projects/{project_id}", headers=auth_headers)
    column_id = detail_response.json()["columns"][0]["id"]

    # 获取当前用户ID
    me_response = client.get("/api/auth/me", headers=auth_headers)
    user_id = me_response.json()["id"]

    # 创建多个任务用于筛选测试
    tasks_data = [
        {"title": "紧急任务", "priority": "high", "assignee_id": user_id},
        {"title": "普通任务", "priority": "medium"},
        {"title": "低优先级任务", "priority": "low"},
        {"title": "带截止日期任务", "due_date": "2025-06-15T12:00:00"},
        {"title": "另一个紧急任务", "priority": "high"},
        {"title": "搜索关键词测试", "priority": "medium"},
    ]

    for task_data in tasks_data:
        client.post(
            f"/api/columns/{column_id}/tasks",
            json=task_data,
            headers=auth_headers,
        )

    return {"project_id": project_id, "column_id": column_id, "user_id": user_id}


class TestTaskFilterByKeyword:
    """关键词筛选测试。"""

    def test_filter_by_keyword_success(self, client, auth_headers, project_with_tasks):
        """测试按关键词筛选成功。"""
        project_id = project_with_tasks["project_id"]

        response = client.get(
            f"/api/projects/{project_id}?keyword=紧急",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        # 统计所有列中的任务
        all_tasks = []
        for column in data["columns"]:
            all_tasks.extend(column["tasks"])

        assert len(all_tasks) == 2
        for task in all_tasks:
            assert "紧急" in task["title"]

    def test_filter_by_keyword_case_insensitive(self, client, auth_headers, project_with_tasks):
        """测试关键词筛选不区分大小写。"""
        project_id = project_with_tasks["project_id"]
        column_id = project_with_tasks["column_id"]

        # 创建英文任务
        client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "Important Task"},
            headers=auth_headers,
        )

        response = client.get(
            f"/api/projects/{project_id}?keyword=important",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        all_tasks = []
        for column in data["columns"]:
            all_tasks.extend(column["tasks"])

        assert len(all_tasks) == 1
        assert all_tasks[0]["title"] == "Important Task"

    def test_filter_by_keyword_no_match(self, client, auth_headers, project_with_tasks):
        """测试关键词无匹配结果。"""
        project_id = project_with_tasks["project_id"]

        response = client.get(
            f"/api/projects/{project_id}?keyword=不存在的关键词",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        all_tasks = []
        for column in data["columns"]:
            all_tasks.extend(column["tasks"])

        assert len(all_tasks) == 0

    def test_filter_by_keyword_special_chars(self, client, auth_headers, project_with_tasks):
        """测试关键词包含特殊字符（LIKE通配符）。"""
        project_id = project_with_tasks["project_id"]
        column_id = project_with_tasks["column_id"]

        # 创建包含特殊字符的任务
        client.post(
            f"/api/columns/{column_id}/tasks",
            json={"title": "100%完成"},
            headers=auth_headers,
        )

        # 搜索包含%的关键词
        response = client.get(
            f"/api/projects/{project_id}?keyword=100%",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        all_tasks = []
        for column in data["columns"]:
            all_tasks.extend(column["tasks"])

        # 应该只匹配包含"100%"的任务，而不是所有任务
        assert len(all_tasks) == 1
        assert all_tasks[0]["title"] == "100%完成"


class TestTaskFilterByPriority:
    """优先级筛选测试。"""

    def test_filter_by_priority_high(self, client, auth_headers, project_with_tasks):
        """测试按高优先级筛选。"""
        project_id = project_with_tasks["project_id"]

        response = client.get(
            f"/api/projects/{project_id}?priority=high",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        all_tasks = []
        for column in data["columns"]:
            all_tasks.extend(column["tasks"])

        assert len(all_tasks) == 2
        for task in all_tasks:
            assert task["priority"] == "high"

    def test_filter_by_priority_medium(self, client, auth_headers, project_with_tasks):
        """测试按中优先级筛选。"""
        project_id = project_with_tasks["project_id"]

        response = client.get(
            f"/api/projects/{project_id}?priority=medium",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        all_tasks = []
        for column in data["columns"]:
            all_tasks.extend(column["tasks"])

        # 有3个medium优先级任务：普通任务、带截止日期任务（默认medium）、搜索关键词测试
        assert len(all_tasks) == 3
        for task in all_tasks:
            assert task["priority"] == "medium"

    def test_filter_by_priority_low(self, client, auth_headers, project_with_tasks):
        """测试按低优先级筛选。"""
        project_id = project_with_tasks["project_id"]

        response = client.get(
            f"/api/projects/{project_id}?priority=low",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        all_tasks = []
        for column in data["columns"]:
            all_tasks.extend(column["tasks"])

        assert len(all_tasks) == 1
        assert all_tasks[0]["priority"] == "low"

    def test_filter_by_invalid_priority(self, client, auth_headers, project_with_tasks):
        """测试无效优先级参数。"""
        project_id = project_with_tasks["project_id"]

        response = client.get(
            f"/api/projects/{project_id}?priority=invalid",
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestTaskFilterByAssignee:
    """负责人筛选测试。"""

    def test_filter_by_assignee_success(self, client, auth_headers, project_with_tasks):
        """测试按负责人筛选成功。"""
        project_id = project_with_tasks["project_id"]
        user_id = project_with_tasks["user_id"]

        response = client.get(
            f"/api/projects/{project_id}?assignee_id={user_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        all_tasks = []
        for column in data["columns"]:
            all_tasks.extend(column["tasks"])

        assert len(all_tasks) == 1
        assert all_tasks[0]["assignee_id"] == user_id

    def test_filter_by_nonexistent_assignee(self, client, auth_headers, project_with_tasks):
        """测试按不存在的负责人筛选。"""
        project_id = project_with_tasks["project_id"]

        response = client.get(
            f"/api/projects/{project_id}?assignee_id=99999",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        all_tasks = []
        for column in data["columns"]:
            all_tasks.extend(column["tasks"])

        assert len(all_tasks) == 0


class TestTaskFilterByDueDate:
    """截止日期筛选测试。"""

    def test_filter_by_due_date_start(self, client, auth_headers, project_with_tasks):
        """测试按截止日期起始筛选。"""
        project_id = project_with_tasks["project_id"]

        response = client.get(
            f"/api/projects/{project_id}?due_date_start=2025-06-01T00:00:00",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        all_tasks = []
        for column in data["columns"]:
            all_tasks.extend(column["tasks"])

        # 只有一个任务有截止日期且在范围内
        assert len(all_tasks) == 1
        assert "2025-06-15" in all_tasks[0]["due_date"]

    def test_filter_by_due_date_end(self, client, auth_headers, project_with_tasks):
        """测试按截止日期结束筛选。"""
        project_id = project_with_tasks["project_id"]

        response = client.get(
            f"/api/projects/{project_id}?due_date_end=2025-06-30T23:59:59",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        all_tasks = []
        for column in data["columns"]:
            all_tasks.extend(column["tasks"])

        assert len(all_tasks) == 1

    def test_filter_by_due_date_range(self, client, auth_headers, project_with_tasks):
        """测试按截止日期范围筛选。"""
        project_id = project_with_tasks["project_id"]

        response = client.get(
            f"/api/projects/{project_id}?due_date_start=2025-06-01&due_date_end=2025-06-30",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        all_tasks = []
        for column in data["columns"]:
            all_tasks.extend(column["tasks"])

        assert len(all_tasks) == 1

    def test_filter_by_due_date_no_match(self, client, auth_headers, project_with_tasks):
        """测试截止日期范围无匹配。"""
        project_id = project_with_tasks["project_id"]

        response = client.get(
            f"/api/projects/{project_id}?due_date_start=2030-01-01&due_date_end=2030-12-31",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        all_tasks = []
        for column in data["columns"]:
            all_tasks.extend(column["tasks"])

        assert len(all_tasks) == 0


class TestTaskFilterCombined:
    """组合筛选测试。"""

    def test_filter_combined_keyword_and_priority(self, client, auth_headers, project_with_tasks):
        """测试关键词和优先级组合筛选。"""
        project_id = project_with_tasks["project_id"]

        response = client.get(
            f"/api/projects/{project_id}?keyword=紧急&priority=high",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        all_tasks = []
        for column in data["columns"]:
            all_tasks.extend(column["tasks"])

        assert len(all_tasks) == 2
        for task in all_tasks:
            assert "紧急" in task["title"]
            assert task["priority"] == "high"

    def test_filter_combined_no_match(self, client, auth_headers, project_with_tasks):
        """测试组合筛选无匹配结果。"""
        project_id = project_with_tasks["project_id"]

        # 搜索"紧急"但优先级为low的任务（不存在）
        response = client.get(
            f"/api/projects/{project_id}?keyword=紧急&priority=low",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        all_tasks = []
        for column in data["columns"]:
            all_tasks.extend(column["tasks"])

        assert len(all_tasks) == 0

    def test_filter_no_params_returns_all(self, client, auth_headers, project_with_tasks):
        """测试无筛选参数返回所有任务。"""
        project_id = project_with_tasks["project_id"]

        response = client.get(
            f"/api/projects/{project_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        all_tasks = []
        for column in data["columns"]:
            all_tasks.extend(column["tasks"])

        assert len(all_tasks) == 6
