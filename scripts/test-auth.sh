#!/bin/bash
# 认证模块测试脚本
cd "$(dirname "$0")/../backend"
pip install pytest-cov -q
python -m pytest tests/ -v --cov=app --cov-report=term-missing
