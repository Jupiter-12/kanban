## ADDED Requirements

### Requirement: 用户注册
系统 MUST 提供用户注册功能，允许新用户创建账号。

#### Scenario: 注册成功
- **WHEN** 用户提供有效的用户名、邮箱和密码
- **THEN** 系统创建新用户账号
- **AND** 返回用户信息（不含密码）

#### Scenario: 用户名已存在
- **WHEN** 用户提供的用户名已被注册
- **THEN** 系统返回错误信息"用户名已存在"

#### Scenario: 邮箱已存在
- **WHEN** 用户提供的邮箱已被注册
- **THEN** 系统返回错误信息"邮箱已存在"

### Requirement: 用户登录
系统 MUST 提供用户登录功能，验证用户身份并返回访问令牌。

#### Scenario: 登录成功
- **WHEN** 用户提供正确的用户名和密码
- **THEN** 系统返回JWT访问令牌
- **AND** 令牌有效期为24小时

#### Scenario: 用户名或密码错误
- **WHEN** 用户提供错误的用户名或密码
- **THEN** 系统返回错误信息"用户名或密码错误"

### Requirement: 获取当前用户
系统 MUST 提供获取当前登录用户信息的功能。

#### Scenario: 获取用户信息成功
- **WHEN** 用户携带有效的JWT令牌请求
- **THEN** 系统返回当前用户的详细信息

#### Scenario: 令牌无效或过期
- **WHEN** 用户携带无效或过期的JWT令牌请求
- **THEN** 系统返回401未授权错误

### Requirement: 用户登出
系统 MUST 提供用户登出功能。

#### Scenario: 登出成功
- **WHEN** 用户请求登出
- **THEN** 系统返回成功响应
- **AND** 前端清除本地存储的令牌

### Requirement: 密码安全存储
系统 MUST 使用bcrypt算法加密存储用户密码。

#### Scenario: 密码加密存储
- **WHEN** 用户注册或修改密码
- **THEN** 系统使用bcrypt对密码进行哈希处理后存储
- **AND** 原始密码不会被存储

### Requirement: 前端认证状态管理
前端 MUST 使用Pinia管理用户认证状态。

#### Scenario: Token持久化
- **WHEN** 用户登录成功
- **THEN** Token存储到localStorage
- **AND** 页面刷新后自动恢复登录状态

#### Scenario: 自动携带Token
- **WHEN** 发送API请求
- **THEN** 请求头自动携带Authorization: Bearer {token}

### Requirement: 路由守卫
前端 MUST 实现路由守卫，保护需要认证的页面。

#### Scenario: 未登录访问受保护页面
- **WHEN** 未登录用户访问需要认证的页面
- **THEN** 自动跳转到登录页

#### Scenario: 已登录访问登录页
- **WHEN** 已登录用户访问登录页
- **THEN** 自动跳转到首页
