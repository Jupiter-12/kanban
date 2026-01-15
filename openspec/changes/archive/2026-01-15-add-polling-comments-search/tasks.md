## 1. 后端实现

### 1.1 评论功能
- [x] 1.1.1 创建 Comment 数据模型（id, task_id, user_id, content, created_at）
- [x] 1.1.2 创建评论 Pydantic Schema
- [x] 1.1.3 实现评论 Service 层（创建、查询、删除）
- [x] 1.1.4 实现评论 API 端点（POST/GET/DELETE）

### 1.2 任务搜索/筛选
- [x] 1.2.1 扩展任务查询 API，支持筛选参数（keyword, assignee_id, priority, due_date_start, due_date_end）
- [x] 1.2.2 实现 Service 层筛选逻辑

## 2. 前端实现

### 2.1 轮询刷新机制
- [x] 2.1.1 创建轮询 composable（usePolling）
- [x] 2.1.2 在看板视图集成轮询逻辑
- [x] 2.1.3 实现页面可见性检测，不可见时暂停轮询

### 2.2 任务评论功能
- [x] 2.2.1 创建评论 API 调用模块
- [x] 2.2.2 创建评论组件（CommentSection.vue）
- [x] 2.2.3 在任务详情弹窗中集成评论区

### 2.3 任务搜索/筛选
- [x] 2.3.1 创建筛选栏组件（TaskFilter.vue）
- [x] 2.3.2 在看板视图集成筛选栏
- [x] 2.3.3 实现筛选状态管理和 API 调用
- [x] 2.3.4 实现筛选结果的实时显示

## 3. 测试

- [x] 3.1 后端评论 API 测试（tests/test_comments.py）
- [x] 3.2 后端任务筛选 API 测试（tests/test_task_filter.py）
- [x] 3.3 前端轮询 composable 测试（usePolling.test.ts）
- [x] 3.4 前端评论 API 测试（comment.api.test.ts）
- [x] 3.5 前端项目 API 筛选参数测试（project.api.test.ts）
- [x] 3.6 前端 board store 测试扩展（board.store.test.ts）
- [x] 3.7 创建一键测试脚本（scripts/test-polling-comments-search.bat/.sh）
