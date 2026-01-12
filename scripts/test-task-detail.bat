@echo off
chcp 65001 >nul
cd /d %~dp0..\backend
pip install pytest-cov -q
python -m pytest tests/test_tasks.py tests/test_users.py -v --cov=app.api.tasks --cov=app.api.users --cov=app.services.task --cov=app.schemas.task --cov=app.models.task --cov-report=term-missing
