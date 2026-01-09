@echo off
chcp 65001 >nul
REM 前端拖拽排序功能测试脚本
cd /d %~dp0..\frontend
call npm test -- --run
