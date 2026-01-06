# 变更：初始化项目框架

## 原因

项目目前只有 openspec 规范文档，缺少实际的代码框架。需要搭建完整的前后端项目结构，引入核心依赖库，为后续功能开发奠定基础。

## 变更内容

### 后端框架初始化
- 创建 FastAPI 项目结构（api/models/services/schemas/utils）
- 配置 SQLAlchemy ORM 和 SQLite 数据库连接
- 引入 JWT 认证和密码加密依赖
- 配置 Ruff 代码检查和 pytest 测试框架
- 创建项目入口文件和基础配置

### 前端框架初始化
- 使用 Vite 创建 Vue 3 + TypeScript 项目
- 引入 Element Plus UI 组件库
- 配置 Pinia 状态管理和 Vue Router 路由
- 引入 Axios HTTP 客户端
- 配置 ESLint 代码检查

### 项目配置
- 创建统一的项目工作区配置
- 配置 .gitignore 文件
- 创建 data/ 目录用于存放 SQLite 数据库文件

## 影响

- 受影响的规格：新增 `project-structure` 能力规格
- 受影响的代码：创建 `backend/` 和 `frontend/` 完整目录结构
