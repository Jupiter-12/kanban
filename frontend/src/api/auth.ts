/**
 * 认证相关API
 */
import { post, get } from './request'
import type { User, UserRegisterRequest, UserLoginRequest, TokenResponse } from '@/types'

/**
 * 用户注册
 * @param data - 注册信息
 */
export function register(data: UserRegisterRequest): Promise<User> {
  return post<User>('/auth/register', data)
}

/**
 * 用户登录
 * @param data - 登录凭据
 */
export function login(data: UserLoginRequest): Promise<TokenResponse> {
  return post<TokenResponse>('/auth/login', data)
}

/**
 * 用户登出
 */
export function logout(): Promise<{ message: string }> {
  return post<{ message: string }>('/auth/logout')
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser(): Promise<User> {
  return get<User>('/auth/me')
}
