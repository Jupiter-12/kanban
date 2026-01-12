/**
 * 项目相关类型定义
 */

import type { UserListItem } from './user'

/** 任务优先级 */
export type TaskPriority = 'high' | 'medium' | 'low'

/** 任务信息 */
export interface Task {
  id: number
  title: string
  description: string | null
  due_date: string | null
  priority: TaskPriority
  assignee_id: number | null
  assignee: UserListItem | null
  column_id: number
  position: number
  created_at: string
  updated_at: string
}

/** 任务创建请求 */
export interface TaskCreateRequest {
  title: string
  description?: string
  due_date?: string
  priority?: TaskPriority
  assignee_id?: number
}

/** 任务更新请求 */
export interface TaskUpdateRequest {
  title?: string
  description?: string | null
  due_date?: string | null
  priority?: TaskPriority
  assignee_id?: number | null
}

/** 看板列信息 */
export interface Column {
  id: number
  name: string
  project_id: number
  position: number
  created_at: string
  updated_at: string
}

/** 看板列（包含任务） */
export interface ColumnWithTasks extends Column {
  tasks: Task[]
}

/** 列创建请求 */
export interface ColumnCreateRequest {
  name: string
}

/** 列更新请求 */
export interface ColumnUpdateRequest {
  name?: string
}

/** 列排序请求 */
export interface ColumnReorderRequest {
  column_ids: number[]
}

/** 任务移动请求 */
export interface TaskMoveRequest {
  target_column_id: number
  position: number
}

/** 项目信息 */
export interface Project {
  id: number
  name: string
  description: string | null
  owner_id: number
  created_at: string
  updated_at: string
}

/** 项目详情（包含列和任务） */
export interface ProjectDetail extends Project {
  columns: ColumnWithTasks[]
}

/** 项目创建请求 */
export interface ProjectCreateRequest {
  name: string
  description?: string
}

/** 项目更新请求 */
export interface ProjectUpdateRequest {
  name?: string
  description?: string
}
