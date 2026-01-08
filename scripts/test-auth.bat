@echo off
chcp 65001 >nul
REM 认证模块测试脚本
cd /d %~dp0..\backend
pip install pytest-cov -q
python -m pytest tests/ -v --cov=app --cov-report=term-missing
