# project-structure Specification

## Purpose
TBD - created by archiving change init-project-scaffold. Update Purpose after archive.
## Requirements
### Requirement: 后端项目结构
系统 MUST 提供符合分层架构的后端项目结构，包含 API 层、Service 层和 Model 层，支持 FastAPI 框架和 SQLAlchemy ORM。

#### Scenario: 后端目录结构完整性
- **WHEN** 开发者查看后端项目目录
- **THEN** 必须存在以下目录结构：
  - `backend/app/api/` - API 路由定义
  - `backend/app/models/` - 数据模型定义
  - `backend/app/services/` - 业务逻辑层
  - `backend/app/schemas/` - Pydantic 数据模型
  - `backend/app/utils/` - 工具函数
  - `backend/tests/` - 测试代码目录
  - `backend/main.py` - 应用入口文件

#### Scenario: 后端依赖配置完整性
- **WHEN** 开发者查看后端依赖配置
- **THEN** pyproject.toml 必须包含以下核心依赖：
  - FastAPI 和 uvicorn（Web 框架）
  - SQLAlchemy（ORM）
  - Pydantic（数据校验）
  - python-jose（JWT 认证）
  - bcrypt（密码加密）
  - ruff（代码检查）
  - pytest 和 httpx（测试）

### Requirement: 前端项目结构
系统 MUST 提供基于 Vue 3 + TypeScript 的前端项目结构，使用 Vite 构建工具，集成 Element Plus 组件库。

#### Scenario: 前端目录结构完整性
- **WHEN** 开发者查看前端项目目录
- **THEN** 必须存在以下目录结构：
  - `frontend/src/api/` - API 调用封装
  - `frontend/src/components/` - 通用组件
  - `frontend/src/views/` - 页面视图
  - `frontend/src/stores/` - Pinia 状态管理
  - `frontend/src/utils/` - 工具函数
  - `frontend/src/router/` - 路由配置

#### Scenario: 前端依赖配置完整性
- **WHEN** 开发者查看前端依赖配置
- **THEN** package.json 必须包含以下核心依赖：
  - Vue 3 和 TypeScript
  - Vite（构建工具）
  - Element Plus（UI 组件库）
  - Pinia（状态管理）
  - Vue Router（路由）
  - Axios（HTTP 客户端）
  - ESLint（代码检查）

### Requirement: 数据库配置
系统 MUST 使用 SQLite 作为数据库，数据文件存放在项目根目录的 data/ 目录下。

#### Scenario: 数据库目录存在
- **WHEN** 应用启动
- **THEN** data/ 目录必须存在并可写入
- **AND** SQLite 数据库文件存储在该目录下

### Requirement: 代码规范配置
系统 MUST 配置统一的代码风格检查工具，确保代码质量一致性。

#### Scenario: 后端代码检查配置
- **WHEN** 开发者运行代码检查
- **THEN** Ruff 必须按照 project.md 中定义的规范进行检查
- **AND** 使用 4 空格缩进，最大行宽 120 字符

#### Scenario: 前端代码检查配置
- **WHEN** 开发者运行代码检查
- **THEN** ESLint 必须按照 project.md 中定义的规范进行检查
- **AND** 使用 2 空格缩进，最大行宽 120 字符

