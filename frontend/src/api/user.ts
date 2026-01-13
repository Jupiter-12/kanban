/**
 * 用户相关API
 */
import { get, put, post, del } from './request'
import type { User, UserListItem, UserRoleUpdateRequest, UserRole, UserInfoUpdateRequest, UserSelfUpdateRequest, UserRegisterRequest } from '@/types'

/**
 * 获取用户列表（用于负责人选择）
 */
export function getUsers(): Promise<UserListItem[]> {
  return get<UserListItem[]>('/users')
}

/**
 * 获取所有用户完整信息（仅所有者可用）
 */
export function getAllUsers(): Promise<User[]> {
  return get<User[]>('/users/all')
}

/**
 * 获取用户详情（仅所有者可用）
 * @param userId - 用户ID
 */
export function getUserDetail(userId: number): Promise<User> {
  return get<User>(`/users/${userId}`)
}

/**
 * 更新用户角色（仅所有者可用）
 * @param userId - 用户ID
 * @param role - 新角色
 */
export function updateUserRole(userId: number, role: UserRole): Promise<User> {
  return put<User>(`/users/${userId}/role`, { role } as UserRoleUpdateRequest)
}

/**
 * 更新用户信息（仅所有者可用）
 * @param userId - 用户ID
 * @param data - 更新数据
 */
export function updateUserInfo(userId: number, data: UserInfoUpdateRequest): Promise<User> {
  return put<User>(`/users/${userId}`, data)
}

/**
 * 创建新用户（仅所有者可用）
 * @param data - 用户创建数据
 */
export function createUser(data: UserRegisterRequest): Promise<User> {
  return post<User>('/users', data)
}

/**
 * 删除用户（仅所有者可用）
 * @param userId - 用户ID
 */
export function deleteUser(userId: number): Promise<void> {
  return del<void>(`/users/${userId}`)
}

/**
 * 获取当前用户个人信息
 */
export function getMyProfile(): Promise<User> {
  return get<User>('/users/me/profile')
}

/**
 * 更新当前用户个人信息
 * @param data - 更新数据
 */
export function updateMyProfile(data: UserSelfUpdateRequest): Promise<User> {
  return put<User>('/users/me/profile', data)
}
