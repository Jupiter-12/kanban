# 看板核心功能技术设计

## 背景

看板系统需要实现项目、列、任务三层数据结构的管理。遵循项目宪章的简单优先原则，采用单体架构和最小依赖策略。

## 目标 / 非目标

### 目标
- 实现项目的 CRUD 操作
- 实现看板列的 CRUD 和排序操作
- 实现任务卡片的 CRUD 操作
- 提供直观的看板视图界面

### 非目标
- 不实现任务拖拽功能（后续迭代）
- 不实现成员管理和任务分配（后续迭代）
- 不实现任务详情（描述、附件、评论等，后续迭代）

## 决策

### 数据模型设计

```
Project (项目)
├── id: int (主键)
├── name: str (项目名称)
├── description: str (项目描述，可选)
├── owner_id: int (创建者ID，外键关联User)
├── created_at: datetime
└── updated_at: datetime

Column (看板列)
├── id: int (主键)
├── name: str (列名称)
├── project_id: int (外键关联Project)
├── position: int (排序位置)
├── created_at: datetime
└── updated_at: datetime

Task (任务卡片)
├── id: int (主键)
├── title: str (任务标题)
├── column_id: int (外键关联Column)
├── position: int (排序位置)
├── created_at: datetime
└── updated_at: datetime
```

### API 设计

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/projects | 创建项目 |
| GET | /api/projects | 获取项目列表 |
| GET | /api/projects/{id} | 获取项目详情（含列和任务） |
| PUT | /api/projects/{id} | 更新项目 |
| DELETE | /api/projects/{id} | 删除项目 |
| POST | /api/projects/{id}/columns | 创建列 |
| PUT | /api/columns/{id} | 更新列 |
| DELETE | /api/columns/{id} | 删除列 |
| PUT | /api/columns/reorder | 批量更新列排序 |
| POST | /api/columns/{id}/tasks | 创建任务 |
| PUT | /api/tasks/{id} | 更新任务 |
| DELETE | /api/tasks/{id} | 删除任务 |

### 前端路由设计

| 路由 | 组件 | 说明 |
|------|------|------|
| /projects | ProjectList | 项目列表页 |
| /projects/:id | BoardView | 看板视图页 |

### 考虑的替代方案

1. **项目和看板分离 vs 项目即看板**
   - 选择：项目即看板（一个项目对应一个看板）
   - 理由：简化数据模型，符合50人小团队的使用场景

2. **列排序使用 position 字段 vs 使用链表结构**
   - 选择：使用 position 整数字段
   - 理由：实现简单，查询高效，50人团队规模下性能足够

## 风险 / 权衡

| 风险 | 缓解措施 |
|------|----------|
| 删除项目会级联删除所有列和任务 | 删除前弹窗确认，提示影响范围 |
| 列排序可能产生 position 冲突 | 使用事务保证原子性，必要时重新计算 position |

## 迁移计划

1. 创建数据库表（projects、columns、tasks）
2. 实现后端 API
3. 实现前端页面和组件
4. 集成测试

## 开放问题

- 无
