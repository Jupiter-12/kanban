/**
 * 用户相关API
 */
import { get } from './request'
import type { UserListItem } from '@/types'

/**
 * 获取用户列表（用于负责人选择）
 */
export function getUsers(): Promise<UserListItem[]> {
  return get<UserListItem[]>('/users')
}
