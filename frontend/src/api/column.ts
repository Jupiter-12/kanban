/**
 * 看板列相关API
 */
import { post, put, del } from './request'
import type {
  Column,
  ColumnCreateRequest,
  ColumnUpdateRequest,
  ColumnReorderRequest
} from '@/types'

/**
 * 创建列
 * @param projectId - 项目ID
 * @param data - 列创建数据
 */
export function createColumn(
  projectId: number,
  data: ColumnCreateRequest
): Promise<Column> {
  return post<Column>(`/projects/${projectId}/columns`, data)
}

/**
 * 更新列
 * @param columnId - 列ID
 * @param data - 列更新数据
 */
export function updateColumn(
  columnId: number,
  data: ColumnUpdateRequest
): Promise<Column> {
  return put<Column>(`/columns/${columnId}`, data)
}

/**
 * 删除列
 * @param columnId - 列ID
 */
export function deleteColumn(columnId: number): Promise<void> {
  return del<void>(`/columns/${columnId}`)
}

/**
 * 重新排序列
 * @param data - 列排序数据
 */
export function reorderColumns(data: ColumnReorderRequest): Promise<Column[]> {
  return put<Column[]>('/columns/reorder', data)
}
