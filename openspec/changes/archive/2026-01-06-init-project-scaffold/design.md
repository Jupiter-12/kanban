# 看板系统设计文档

## 1. 数据模型设计

### 1.1 用户表 (users)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 用户ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| email | VARCHAR(100) | UNIQUE, NOT NULL | 邮箱 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 |
| display_name | VARCHAR(100) | | 显示名称 |
| avatar_url | VARCHAR(255) | | 头像URL |
| is_active | BOOLEAN | DEFAULT TRUE | 是否激活 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 1.2 看板表 (boards)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 看板ID |
| name | VARCHAR(100) | NOT NULL | 看板名称 |
| description | TEXT | | 看板描述 |
| owner_id | INTEGER | FOREIGN KEY | 所有者ID |
| is_archived | BOOLEAN | DEFAULT FALSE | 是否归档 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 1.3 看板成员表 (board_members)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 记录ID |
| board_id | INTEGER | FOREIGN KEY | 看板ID |
| user_id | INTEGER | FOREIGN KEY | 用户ID |
| role | VARCHAR(20) | NOT NULL | 角色(admin/member) |
| created_at | DATETIME | NOT NULL | 加入时间 |

### 1.4 列表表 (columns)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 列表ID |
| board_id | INTEGER | FOREIGN KEY | 所属看板ID |
| name | VARCHAR(100) | NOT NULL | 列表名称 |
| position | INTEGER | NOT NULL | 排序位置 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 1.5 任务表 (tasks)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 任务ID |
| column_id | INTEGER | FOREIGN KEY | 所属列表ID |
| title | VARCHAR(200) | NOT NULL | 任务标题 |
| description | TEXT | | 任务描述 |
| assignee_id | INTEGER | FOREIGN KEY | 负责人ID |
| priority | VARCHAR(20) | DEFAULT 'medium' | 优先级(low/medium/high/urgent) |
| due_date | DATE | | 截止日期 |
| position | INTEGER | NOT NULL | 排序位置 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 1.6 任务标签表 (labels)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 标签ID |
| board_id | INTEGER | FOREIGN KEY | 所属看板ID |
| name | VARCHAR(50) | NOT NULL | 标签名称 |
| color | VARCHAR(20) | NOT NULL | 标签颜色 |

### 1.7 任务-标签关联表 (task_labels)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| task_id | INTEGER | FOREIGN KEY | 任务ID |
| label_id | INTEGER | FOREIGN KEY | 标签ID |

### 1.8 评论表 (comments)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 评论ID |
| task_id | INTEGER | FOREIGN KEY | 任务ID |
| user_id | INTEGER | FOREIGN KEY | 评论者ID |
| content | TEXT | NOT NULL | 评论内容 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 1.9 操作日志表 (activity_logs)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 日志ID |
| board_id | INTEGER | FOREIGN KEY | 看板ID |
| user_id | INTEGER | FOREIGN KEY | 操作者ID |
| action | VARCHAR(50) | NOT NULL | 操作类型 |
| target_type | VARCHAR(50) | NOT NULL | 目标类型 |
| target_id | INTEGER | NOT NULL | 目标ID |
| details | TEXT | | 操作详情(JSON) |
| created_at | DATETIME | NOT NULL | 操作时间 |

---

## 2. API 接口设计

### 2.1 认证模块 (/api/auth)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录 |
| POST | /api/auth/logout | 用户登出 |
| GET | /api/auth/me | 获取当前用户信息 |
| PUT | /api/auth/password | 修改密码 |

### 2.2 用户模块 (/api/users)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/users | 获取用户列表 |
| GET | /api/users/{id} | 获取用户详情 |
| PUT | /api/users/{id} | 更新用户信息 |

### 2.3 看板模块 (/api/boards)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/boards | 获取看板列表 |
| POST | /api/boards | 创建看板 |
| GET | /api/boards/{id} | 获取看板详情 |
| PUT | /api/boards/{id} | 更新看板 |
| DELETE | /api/boards/{id} | 删除看板 |
| GET | /api/boards/{id}/members | 获取看板成员 |
| POST | /api/boards/{id}/members | 添加看板成员 |
| DELETE | /api/boards/{id}/members/{user_id} | 移除看板成员 |

### 2.4 列表模块 (/api/columns)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/boards/{board_id}/columns | 获取列表 |
| POST | /api/boards/{board_id}/columns | 创建列表 |
| PUT | /api/columns/{id} | 更新列表 |
| DELETE | /api/columns/{id} | 删除列表 |
| PUT | /api/columns/{id}/position | 调整列表位置 |

### 2.5 任务模块 (/api/tasks)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/columns/{column_id}/tasks | 获取任务列表 |
| POST | /api/columns/{column_id}/tasks | 创建任务 |
| GET | /api/tasks/{id} | 获取任务详情 |
| PUT | /api/tasks/{id} | 更新任务 |
| DELETE | /api/tasks/{id} | 删除任务 |
| PUT | /api/tasks/{id}/move | 移动任务(跨列表) |
| PUT | /api/tasks/{id}/position | 调整任务位置 |
| PUT | /api/tasks/{id}/assignee | 分配负责人 |

### 2.6 标签模块 (/api/labels)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/boards/{board_id}/labels | 获取标签列表 |
| POST | /api/boards/{board_id}/labels | 创建标签 |
| PUT | /api/labels/{id} | 更新标签 |
| DELETE | /api/labels/{id} | 删除标签 |
| POST | /api/tasks/{task_id}/labels/{label_id} | 添加任务标签 |
| DELETE | /api/tasks/{task_id}/labels/{label_id} | 移除任务标签 |

### 2.7 评论模块 (/api/comments)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/tasks/{task_id}/comments | 获取任务评论 |
| POST | /api/tasks/{task_id}/comments | 添加评论 |
| PUT | /api/comments/{id} | 更新评论 |
| DELETE | /api/comments/{id} | 删除评论 |

### 2.8 活动日志模块 (/api/activities)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/boards/{board_id}/activities | 获取看板活动日志 |

---

## 3. 前端页面设计

### 3.0 布局规范

#### 目标平台
- **仅支持桌面端**，不需要考虑移动端适配

#### 布局要求

| 项目 | 规范 |
|------|------|
| 布局方式 | 响应式 + 流式布局 |
| 滚动条 | 特殊情况下启用垂直和水平滚动条 |
| 最小宽度 | 根据内容需要设定合理的最小宽度 |

#### 布局原则
- 优先使用响应式布局，适应不同桌面分辨率
- 采用流式布局，内容随容器宽度自适应
- 仅在内容超出视口时显示滚动条
- 避免固定宽度，优先使用百分比或弹性布局

### 3.1 页面结构

| 页面 | 路由 | 说明 |
|------|------|------|
| 登录页 | /login | 用户登录 |
| 注册页 | /register | 用户注册 |
| 首页 | / | 看板列表 |
| 看板页 | /boards/{id} | 看板详情/任务管理 |
| 个人设置 | /settings | 个人信息设置 |

### 3.2 组件划分

#### 布局组件

| 组件 | 说明 |
|------|------|
| AppLayout | 应用主布局(导航栏+侧边栏+内容区) |
| AppHeader | 顶部导航栏 |
| AppSidebar | 侧边栏(看板列表) |

#### 看板组件

| 组件 | 说明 |
|------|------|
| BoardList | 看板列表(首页) |
| BoardCard | 看板卡片 |
| BoardView | 看板视图(包含列表和任务) |
| BoardHeader | 看板头部(名称、成员、设置) |
| BoardSettings | 看板设置弹窗 |
| MemberList | 成员列表 |
| MemberAvatar | 成员头像 |

#### 列表组件

| 组件 | 说明 |
|------|------|
| ColumnList | 列表容器(水平滚动) |
| ColumnCard | 单个列表(包含任务卡片) |
| ColumnHeader | 列表头部(名称、菜单) |
| AddColumn | 添加列表按钮 |

#### 任务组件

| 组件 | 说明 |
|------|------|
| TaskCard | 任务卡片(可拖拽) |
| TaskDetail | 任务详情弹窗 |
| TaskForm | 任务编辑表单 |
| AddTask | 添加任务按钮/表单 |
| TaskLabels | 任务标签显示 |
| TaskDueDate | 截止日期显示 |
| TaskAssignee | 负责人显示 |

#### 评论组件

| 组件 | 说明 |
|------|------|
| CommentList | 评论列表 |
| CommentItem | 单条评论 |
| CommentForm | 评论输入框 |

#### 通用组件

| 组件 | 说明 |
|------|------|
| LabelTag | 标签标记 |
| LabelPicker | 标签选择器 |
| UserPicker | 用户选择器 |
| DatePicker | 日期选择器 |
| PriorityTag | 优先级标记 |
| ConfirmDialog | 确认对话框 |
| LoadingSpinner | 加载指示器 |

### 3.3 状态管理 (Pinia Stores)

| Store | 说明 |
|------|------|
| useAuthStore | 认证状态(用户信息、token) |
| useBoardStore | 看板状态(看板列表、当前看板) |
| useColumnStore | 列表状态(列表数据) |
| useTaskStore | 任务状态(任务数据) |
| useLabelStore | 标签状态(标签数据) |

---

## 4. 数据流设计

### 4.1 认证流程

```
用户登录 -> POST /api/auth/login -> 返回JWT Token
    -> 存储Token到localStorage
    -> 后续请求携带Authorization Header
```

### 4.2 看板数据加载流程

```
进入看板页 -> GET /api/boards/{id}
    -> 获取看板详情(包含成员)
    -> GET /api/boards/{id}/columns
    -> 获取所有列表及其任务
    -> 渲染看板视图
```

### 4.3 任务拖拽流程

```
拖拽任务 -> 本地更新位置(乐观更新)
    -> PUT /api/tasks/{id}/move 或 /position
    -> 成功: 保持本地状态
    -> 失败: 回滚本地状态，显示错误
```

### 4.4 数据刷新机制

```
采用轮询方式(5-10秒间隔)刷新看板数据
    -> 对比本地数据与服务器数据
    -> 增量更新变化的部分
    -> 避免全量刷新导致的闪烁
```

---

## 5. 安全设计

### 5.1 认证机制

- JWT Token 有效期：24小时
- Token 存储：localStorage
- 刷新机制：Token 过期后重新登录

### 5.2 权限控制

| 角色 | 权限 |
|------|------|
| 看板管理员(admin) | 管理成员、删除看板、所有操作 |
| 看板成员(member) | 创建/编辑/删除任务、评论 |
| 非成员 | 无法访问看板 |

### 5.3 数据校验

- 前端：表单验证(必填项、格式检查)
- 后端：Pydantic 模型校验
- 数据库：外键约束、唯一约束
