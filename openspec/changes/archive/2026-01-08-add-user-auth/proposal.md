# 变更：添加用户认证功能

## 原因

看板系统需要用户认证功能，以便用户能够注册账号、登录系统，并在后续功能中实现基于用户的权限控制和数据隔离。这是系统的基础能力，所有其他功能都依赖于此。

## 变更内容

### 后端认证模块
- 创建用户数据模型（User表）
- 实现密码加密存储（bcrypt）
- 实现JWT Token生成和验证
- 创建认证API接口（注册/登录/登出/获取当前用户）
- 实现认证依赖注入（get_current_user）

### 前端认证模块
- 创建认证状态管理（Auth Store）
- 实现Token持久化（localStorage）
- 完善HTTP拦截器（自动携带Token、401处理）
- 创建登录页面
- 创建注册页面
- 实现路由守卫（未登录跳转）
- 创建主布局框架（导航栏、用户信息）

## 影响

- 受影响的规格：新增 `user-auth` 能力规格
- 受影响的代码：
  - `backend/app/models/user.py` - 用户模型
  - `backend/app/schemas/user.py` - 用户Schema
  - `backend/app/services/auth.py` - 认证服务
  - `backend/app/api/auth.py` - 认证API
  - `backend/app/utils/security.py` - 安全工具
  - `backend/app/deps.py` - 依赖注入
  - `frontend/src/stores/auth.ts` - 认证状态
  - `frontend/src/api/auth.ts` - 认证API
  - `frontend/src/views/Login.vue` - 登录页
  - `frontend/src/views/Register.vue` - 注册页
  - `frontend/src/components/layout/` - 布局组件
  - `frontend/src/router/index.ts` - 路由守卫
