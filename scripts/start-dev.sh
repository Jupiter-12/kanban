#!/bin/bash

echo "========================================"
echo "  Kanban System - Dev Environment"
echo "========================================"
echo ""

# 检查目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 清理函数 - 退出时终止所有子进程
cleanup() {
    echo ""
    echo "正在停止服务..."
    # 终止整个进程组
    pkill -P $$ 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "[1/2] 启动后端服务 (端口 8000)..."
cd backend
# 使用 stdbuf 禁用缓冲，确保日志实时输出
python -u -m uvicorn main:app --reload --reload-exclude tests --host 0.0.0.0 --port 8000 2>&1 &
BACKEND_PID=$!
cd ..

echo "[2/2] 启动前端服务 (端口 5173)..."
sleep 2
cd frontend
npm run dev 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "  服务已启动!"
echo "========================================"
echo ""
echo "  后端 API: http://localhost:8000"
echo "  API 文档: http://localhost:8000/docs"
echo "  前端页面: http://localhost:5173"
echo ""
echo "  按 Ctrl+C 停止所有服务"
echo ""

# 等待所有子进程
wait
