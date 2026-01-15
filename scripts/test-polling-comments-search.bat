@echo off
chcp 65001 >nul
REM 轮询刷新、评论、搜索筛选功能测试脚本

echo ========================================
echo 后端测试
echo ========================================
cd /d %~dp0..\backend
pip install pytest-cov -q
python -m pytest tests/test_comments.py tests/test_task_filter.py -v --cov=app.api.comments --cov=app.services.comment --cov=app.models.comment --cov=app.schemas.comment --cov=app.services.project --cov-report=term-missing

echo.
echo ========================================
echo 前端测试
echo ========================================
cd /d %~dp0..\frontend
call npm run test -- --run --coverage --coverage.include="src/api/comment.ts" --coverage.include="src/api/project.ts" --coverage.include="src/composables/usePolling.ts" --coverage.include="src/stores/board.ts"
