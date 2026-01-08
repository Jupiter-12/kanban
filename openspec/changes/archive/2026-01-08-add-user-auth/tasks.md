## 1. 后端用户模型

- [x] 1.1 创建用户模型 `backend/app/models/user.py`
- [x] 1.2 创建用户Schema `backend/app/schemas/user.py`

## 2. 后端安全工具

- [x] 2.1 创建密码加密工具 `backend/app/utils/security.py`
- [x] 2.2 创建JWT工具 `backend/app/utils/security.py`
- [x] 2.3 创建配置管理 `backend/app/config.py`

## 3. 后端认证服务

- [x] 3.1 创建认证服务 `backend/app/services/auth.py`
- [x] 3.2 创建认证依赖 `backend/app/deps.py`

## 4. 后端认证API

- [x] 4.1 创建认证路由 `backend/app/api/auth.py`
- [x] 4.2 注册路由到主应用
- [x] 4.3 初始化数据库表

## 5. 前端认证状态

- [x] 5.1 创建类型定义 `frontend/src/types/`
- [x] 5.2 创建认证Store `frontend/src/stores/auth.ts`
- [x] 5.3 创建认证API `frontend/src/api/auth.ts`

## 6. 前端HTTP拦截器

- [x] 6.1 完善请求拦截器（自动携带Token）
- [x] 6.2 完善响应拦截器（401跳转登录）

## 7. 前端页面

- [x] 7.1 创建登录页 `frontend/src/views/LoginView.vue`
- [x] 7.2 创建注册页 `frontend/src/views/RegisterView.vue`
- [x] 7.3 创建主布局 `frontend/src/components/layout/AppLayout.vue`
- [x] 7.4 创建导航栏 `frontend/src/components/layout/AppHeader.vue`
- [x] 7.5 更新首页 `frontend/src/views/HomeView.vue`

## 8. 前端路由

- [x] 8.1 配置路由守卫
- [x] 8.2 添加登录/注册路由

## 9. 测试

- [x] 9.1 后端认证API测试
- [x] 9.2 前端登录流程测试（手动验证通过）
