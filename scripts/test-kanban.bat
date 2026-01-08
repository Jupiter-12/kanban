@echo off
chcp 65001 >nul
REM 看板核心模块测试脚本
cd /d %~dp0..\backend
pip install pytest-cov -q
python -m pytest tests/test_projects.py tests/test_columns.py tests/test_tasks.py -v --cov=app.api.projects --cov=app.api.columns --cov=app.api.tasks --cov=app.services.project --cov=app.services.column --cov=app.services.task --cov-report=term-missing
