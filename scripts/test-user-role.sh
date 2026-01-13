#!/bin/bash
# 用户角色权限测试脚本 (add-project-member 提案)
cd "$(dirname "$0")/../backend"
pip install pytest-cov -q
python -m pytest tests/test_users.py tests/test_projects.py::TestProjectRolePermissions -v --cov=app.api.users --cov=app.api.projects --cov-report=term-missing
