# 变更：添加拖拽排序功能

## 原因

看板系统的核心交互是通过拖拽来调整任务和列的顺序。当前系统已有后端排序接口，但前端缺少拖拽交互功能，用户无法直观地调整任务位置和列顺序。

## 变更内容

- 添加任务拖拽排序功能（列内拖拽 + 跨列拖拽）
- 添加列拖拽排序功能
- 前端集成 vuedraggable 拖拽库
- 补充任务移动 API 封装（后端接口已存在）

## 影响

- 受影响的规格：kanban-core
- 受影响的代码：
  - `frontend/src/views/BoardView.vue` - 看板视图页
  - `frontend/src/components/BoardColumn.vue` - 看板列组件
  - `frontend/src/api/task.ts` - 任务 API（新增 moveTask）
  - `frontend/src/stores/board.ts` - 看板状态管理
  - `frontend/package.json` - 新增 vuedraggable 依赖
