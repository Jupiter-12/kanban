## 背景

当前看板系统已实现基础的任务管理功能，但缺少：
1. 多用户协作时的数据同步机制
2. 任务讨论功能
3. 任务快速查找能力

## 目标 / 非目标

### 目标
- 实现5-10秒轮询刷新，保证多用户数据一致性
- 提供任务评论功能，支持团队讨论
- 提供任务搜索筛选，提高查找效率

### 非目标
- 不实现 WebSocket 实时推送（遵循项目宪章最小依赖原则）
- 不实现评论@提及功能（后续迭代）
- 不实现评论编辑功能（保持简单）

## 技术决策

### 轮询刷新
- **决策**：使用 setInterval + Page Visibility API
- **理由**：简单可靠，无需额外依赖，符合项目宪章

### 评论存储
- **决策**：新建 comments 表，外键关联 tasks 和 users
- **理由**：标准关系型设计，便于查询和维护

### 筛选实现
- **决策**：后端 API 支持筛选参数，前端传参查询
- **理由**：减少前端数据处理，支持大数据量场景

## 数据模型

### Comment 表
```sql
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_comments_task_id ON comments(task_id);
```

## API 设计

### 评论 API
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/tasks/{task_id}/comments | 获取任务评论列表 |
| POST | /api/tasks/{task_id}/comments | 添加评论 |
| DELETE | /api/comments/{comment_id} | 删除评论（仅自己的） |

### 任务筛选参数
| 参数 | 类型 | 说明 |
|------|------|------|
| keyword | string | 标题关键词（模糊匹配） |
| assignee_id | int | 负责人ID |
| priority | string | 优先级（high/medium/low） |
| due_date_start | date | 截止日期起始 |
| due_date_end | date | 截止日期结束 |

## 风险 / 权衡

| 风险 | 缓解措施 |
|------|----------|
| 轮询增加服务器负载 | 页面不可见时暂停轮询；合理设置刷新间隔 |
| 评论数据量增长 | 分页加载；定期清理过期评论（可选） |

## 开放问题

- 无
