# 变更：添加任务详情增强功能

## 原因

当前看板系统的任务卡片只有标题字段，无法记录任务的详细信息。用户需要为任务添加描述、设置截止日期、指定优先级和指派负责人，以便更好地管理和跟踪任务进度。

## 变更内容

### 后端任务详情扩展
- 扩展任务数据模型，添加描述、截止日期、优先级、负责人字段
- 更新任务API接口，支持新字段的创建和更新
- 添加获取用户列表接口（用于负责人选择）

### 前端任务详情功能
- 创建任务详情弹窗组件
- 支持编辑任务描述（富文本或纯文本）
- 支持设置截止日期（日期选择器）
- 支持设置优先级（高/中/低）
- 支持指派负责人（下拉选择项目成员）
- 任务卡片展示优先级标识和截止日期

## 影响

- 受影响的规格：`kanban-core`
- 受影响的代码：
  - `backend/app/models/task.py` - 任务模型扩展
  - `backend/app/schemas/task.py` - 任务Schema扩展
  - `backend/app/services/task.py` - 任务服务扩展
  - `backend/app/api/tasks.py` - 任务API扩展
  - `backend/app/api/users.py` - 新增用户列表API
  - `frontend/src/components/TaskDetailDialog.vue` - 新增任务详情弹窗
  - `frontend/src/components/TaskCard.vue` - 任务卡片展示增强
  - `frontend/src/api/task.ts` - 任务API扩展
  - `frontend/src/api/user.ts` - 新增用户API
  - `frontend/src/types/task.ts` - 任务类型扩展
