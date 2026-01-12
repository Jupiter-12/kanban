#!/bin/bash
# 任务详情功能测试脚本（含覆盖率报告）
cd "$(dirname "$0")/../backend"
pip install pytest-cov -q
python -m pytest tests/test_tasks.py tests/test_users.py -v --cov=app.api.tasks --cov=app.api.users --cov=app.services.task --cov=app.schemas.task --cov=app.models.task --cov-report=term-missing
