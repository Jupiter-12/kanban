/**
 * 用户相关类型定义
 */

/** 用户信息 */
export interface User {
  id: number
  username: string
  email: string
  display_name: string | null
  avatar_url: string | null
  is_active: boolean
  created_at: string
  updated_at: string
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
