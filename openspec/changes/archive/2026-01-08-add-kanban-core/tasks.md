# 实施任务清单

## 1. 后端数据模型

- [x] 1.1 创建 Project 模型（backend/app/models/project.py）
- [x] 1.2 创建 Column 模型（backend/app/models/column.py）
- [x] 1.3 创建 Task 模型（backend/app/models/task.py）
- [x] 1.4 更新 models/__init__.py 导出新模型

## 2. 后端 Schema

- [x] 2.1 创建 Project Schema（backend/app/schemas/project.py）
- [x] 2.2 创建 Column Schema（backend/app/schemas/column.py）
- [x] 2.3 创建 Task Schema（backend/app/schemas/task.py）

## 3. 后端 Service

- [x] 3.1 创建 ProjectService（backend/app/services/project.py）
- [x] 3.2 创建 ColumnService（backend/app/services/column.py）
- [x] 3.3 创建 TaskService（backend/app/services/task.py）

## 4. 后端 API

- [x] 4.1 创建项目 API 路由（backend/app/api/projects.py）
- [x] 4.2 创建列 API 路由（backend/app/api/columns.py）
- [x] 4.3 创建任务 API 路由（backend/app/api/tasks.py）
- [x] 4.4 注册路由到主应用

## 5. 后端测试

- [x] 5.1 编写项目 API 测试
- [x] 5.2 编写列 API 测试
- [x] 5.3 编写任务 API 测试

## 6. 前端 API 封装

- [x] 6.1 创建项目 API（frontend/src/api/project.ts）
- [x] 6.2 创建列 API（frontend/src/api/column.ts）
- [x] 6.3 创建任务 API（frontend/src/api/task.ts）

## 7. 前端状态管理

- [x] 7.1 创建项目 Store（frontend/src/stores/project.ts）
- [x] 7.2 创建看板 Store（frontend/src/stores/board.ts）

## 8. 前端页面和组件

- [x] 8.1 创建项目列表页（frontend/src/views/ProjectList.vue）
- [x] 8.2 创建看板视图页（frontend/src/views/BoardView.vue）
- [x] 8.3 创建项目卡片组件（frontend/src/components/ProjectCard.vue）
- [x] 8.4 创建看板列组件（frontend/src/components/BoardColumn.vue）
- [x] 8.5 创建任务卡片组件（frontend/src/components/TaskCard.vue）
- [x] 8.6 创建项目对话框组件（frontend/src/components/ProjectDialog.vue）

## 9. 前端路由

- [x] 9.1 添加项目列表路由
- [x] 9.2 添加看板视图路由
- [x] 9.3 更新导航菜单
