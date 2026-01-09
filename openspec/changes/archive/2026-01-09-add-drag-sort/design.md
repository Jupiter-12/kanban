## 背景

看板系统需要拖拽排序功能来提升用户体验。后端已预留完整的排序接口，前端需要集成拖拽库实现交互。

**约束：**
- 遵循项目宪章的简单优先原则
- 使用成熟稳定的拖拽库
- 保持与现有代码风格一致

## 目标 / 非目标

**目标：**
- 实现任务列内拖拽排序
- 实现任务跨列拖拽移动
- 实现列拖拽排序
- 拖拽操作实时同步到后端

**非目标：**
- 多选拖拽（一次拖拽多个任务）
- 拖拽动画优化
- 触摸设备支持（项目仅支持桌面端）

## 决策

### 拖拽库选择：vuedraggable

**选择理由：**
- Vue 3 官方推荐的拖拽库
- 基于 Sortable.js，成熟稳定
- 支持列表内排序和跨列表拖拽
- API 简洁，学习成本低

**考虑的替代方案：**
- `@vueuse/integrations/useSortable` - 功能较基础，跨列拖拽支持不够完善
- 原生 HTML5 Drag API - 需要大量封装，开发成本高
- `vue-smooth-dnd` - 维护不活跃

### 拖拽实现方案

**任务拖拽：**
- 使用 vuedraggable 的 `group` 属性实现跨列拖拽
- 监听 `change` 事件获取拖拽结果
- 调用 `PUT /tasks/{task_id}/move` 接口同步

**列拖拽：**
- 使用 vuedraggable 包裹列容器
- 监听 `end` 事件获取新顺序
- 调用 `PUT /columns/reorder` 接口同步

### 状态同步策略

**乐观更新：**
- 拖拽结束立即更新本地状态
- 异步调用后端接口
- 失败时回滚并提示错误

## 风险 / 权衡

| 风险 | 缓解措施 |
|------|----------|
| 拖拽过程中网络请求失败 | 乐观更新 + 失败回滚 + 错误提示 |
| 多用户同时操作冲突 | 当前版本不处理，后续可通过轮询刷新解决 |
| 大量任务时性能问题 | vuedraggable 内置虚拟滚动支持，暂不启用 |

## 技术细节

### 依赖版本

```json
{
  "vuedraggable": "^4.1.0"
}
```

### 关键代码结构

```
frontend/src/
├── api/
│   └── task.ts          # 新增 moveTask 函数
├── types/
│   └── project.ts       # 新增 TaskMoveRequest 类型
├── stores/
│   └── board.ts         # 新增 moveTask、reorderColumns 方法
├── components/
│   └── BoardColumn.vue  # 集成 vuedraggable 实现任务拖拽
└── views/
    └── BoardView.vue    # 集成 vuedraggable 实现列拖拽
```

## 开放问题

无
