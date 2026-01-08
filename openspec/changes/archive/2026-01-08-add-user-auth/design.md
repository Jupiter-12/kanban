## 背景

用户认证是看板系统的基础能力，涉及安全敏感操作（密码存储、令牌管理）。需要在实施前明确技术决策，确保安全性和一致性。

## 目标 / 非目标

**目标：**
- 实现安全的用户注册和登录
- 实现JWT令牌认证机制
- 实现前端认证状态管理和路由守卫

**非目标：**
- 不实现OAuth第三方登录
- 不实现邮箱验证
- 不实现密码找回功能
- 不实现Token刷新机制（过期后重新登录）

## 决策

### 1. 密码加密方案

**决策**：使用bcrypt算法

**原因**：
- bcrypt专为密码哈希设计，内置盐值
- 计算成本可调，抵抗暴力破解
- 项目宪章已指定使用bcrypt

### 2. JWT令牌方案

**决策**：使用python-jose库，HS256算法

**原因**：
- 项目宪章已指定使用python-jose
- HS256对称加密，单体应用足够安全
- 令牌有效期24小时，过期后重新登录

**令牌结构**：
```json
{
  "sub": "user_id",
  "exp": "过期时间戳"
}
```

### 3. 前端Token存储

**决策**：使用localStorage

**原因**：
- 项目宪章已指定使用localStorage
- 简单直接，刷新页面不丢失
- 配合路由守卫实现认证保护

### 4. API接口设计

**决策**：遵循设计文档中的API规范

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录 |
| POST | /api/auth/logout | 用户登出 |
| GET | /api/auth/me | 获取当前用户 |

### 5. 用户模型设计

**决策**：遵循设计文档中的数据模型

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(50) | 用户名，唯一 |
| email | VARCHAR(100) | 邮箱，唯一 |
| password_hash | VARCHAR(255) | 密码哈希 |
| display_name | VARCHAR(100) | 显示名称 |
| avatar_url | VARCHAR(255) | 头像URL |
| is_active | BOOLEAN | 是否激活 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

## 风险 / 权衡

| 风险 | 缓解措施 |
|------|----------|
| JWT令牌泄露 | 设置合理过期时间（24小时） |
| 密码暴力破解 | bcrypt计算成本 + 后续可加登录限流 |
| XSS窃取Token | 前端输入转义 + CSP策略 |

## 开放问题

无
