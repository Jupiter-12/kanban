/**
 * 用户相关类型定义
 */

/** 用户角色枚举 */
export type UserRole = 'owner' | 'admin' | 'user'

/** 用户信息 */
export interface User {
  id: number
  username: string
  email: string
  display_name: string | null
  avatar_url: string | null
  role: UserRole
  is_active: boolean
  created_at: string
  updated_at: string
}

/** 用户列表项（用于负责人选择） */
export interface UserListItem {
  id: number
  username: string
  display_name: string | null
  role: UserRole
}

/** 用户角色更新请求 */
export interface UserRoleUpdateRequest {
  role: UserRole
}

/** 用户信息更新请求 */
export interface UserInfoUpdateRequest {
  display_name?: string
  email?: string
  password?: string
  is_active?: boolean
}

/** 用户个人信息更新请求 */
export interface UserSelfUpdateRequest {
  display_name?: string
  email?: string
  current_password?: string
  new_password?: string
}

/** 用户注册请求 */
export interface UserRegisterRequest {
  username: string
  email: string
  password: string
  display_name?: string
}

/** 用户登录请求 */
export interface UserLoginRequest {
  username: string
  password: string
}

/** 令牌响应 */
export interface TokenResponse {
  access_token: string
  token_type: string
}
