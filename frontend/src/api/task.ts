/**
 * 任务相关API
 */
import { post, put, del } from './request'
import type { Task, TaskCreateRequest, TaskUpdateRequest, TaskMoveRequest } from '@/types'

/**
 * 创建任务
 * @param columnId - 列ID
 * @param data - 任务创建数据
 */
export function createTask(
  columnId: number,
  data: TaskCreateRequest
): Promise<Task> {
  return post<Task>(`/columns/${columnId}/tasks`, data)
}

/**
 * 更新任务
 * @param taskId - 任务ID
 * @param data - 任务更新数据
 */
export function updateTask(
  taskId: number,
  data: TaskUpdateRequest
): Promise<Task> {
  return put<Task>(`/tasks/${taskId}`, data)
}

/**
 * 删除任务
 * @param taskId - 任务ID
 */
export function deleteTask(taskId: number): Promise<void> {
  return del<void>(`/tasks/${taskId}`)
}

/**
 * 移动任务
 * @param taskId - 任务ID
 * @param data - 移动数据（目标列ID和位置）
 */
export function moveTask(
  taskId: number,
  data: TaskMoveRequest
): Promise<Task> {
  return put<Task>(`/tasks/${taskId}/move`, data)
}
