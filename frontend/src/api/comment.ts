/**
 * 评论相关API
 */
import { get, post, del } from './request'
import type { Comment, CommentCreateRequest } from '@/types'

/**
 * 获取任务评论列表
 * @param taskId - 任务ID
 */
export function getComments(taskId: number): Promise<Comment[]> {
  return get<Comment[]>(`/tasks/${taskId}/comments`)
}

/**
 * 添加评论
 * @param taskId - 任务ID
 * @param data - 评论创建数据
 */
export function createComment(
  taskId: number,
  data: CommentCreateRequest
): Promise<Comment> {
  return post<Comment>(`/tasks/${taskId}/comments`, data)
}

/**
 * 删除评论
 * @param commentId - 评论ID
 */
export function deleteComment(commentId: number): Promise<void> {
  return del<void>(`/comments/${commentId}`)
}
