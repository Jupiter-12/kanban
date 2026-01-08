/**
 * 认证状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, UserLoginRequest, UserRegisterRequest } from '@/types'
import * as authApi from '@/api/auth'

/** Token存储键名 */
const TOKEN_KEY = 'kanban_token'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const currentUser = computed(() => user.value)

  /** 
   * 设置Token 
   */ 
  function setToken(newToken: string | null) { 
    token.value = newToken
    if (newToken) {
      localStorage.setItem(TOKEN_KEY, newToken)
    } else {
      localStorage.removeItem(TOKEN_KEY)
    }
  } 

  /** 
   * 判断是否为未认证错误 
   */ 
  function isUnauthorized(error: unknown): boolean { 
    const status = (error as { response?: { status?: number } })?.response?.status 
    return status === 401 
  } 

  /**
   * 用户注册
   */
  async function register(data: UserRegisterRequest): Promise<User> {
    loading.value = true
    try {
      const newUser = await authApi.register(data)
      return newUser
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户登录
   */
  async function login(data: UserLoginRequest): Promise<void> {
    loading.value = true
    try {
      const response = await authApi.login(data)
      setToken(response.access_token)
      await fetchCurrentUser()
    } catch (error) {
      // 登录流程异常时回滚登录态
      setToken(null)
      user.value = null
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户登出
   */
  async function logout(): Promise<void> {
    try {
      await authApi.logout()
    } finally {
      setToken(null)
      user.value = null
    }
  }

  /**
   * 获取当前用户信息
   */
  async function fetchCurrentUser(): Promise<void> {
    if (!token.value) {
      user.value = null
      return
    }
    try {
      user.value = await authApi.getCurrentUser()
    } catch (error) {
      if (isUnauthorized(error)) {
        // Token无效，清除
        setToken(null)
        user.value = null
      } else {
        throw error
      }
    }
  }

  /**
   * 初始化认证状态
   */
  async function initAuth(): Promise<void> {
    if (token.value) {
      try {
        await fetchCurrentUser()
      } catch (error) {
        // 如果是401错误，说明token无效，清除登录态
        if (isUnauthorized(error)) {
          setToken(null)
          user.value = null
        }
        // 其他错误（如网络错误）保留token，避免因为瞬时错误导致误登出
      }
    }
  }

  return {
    // 状态
    user,
    token,
    loading,
    // 计算属性
    isAuthenticated,
    currentUser,
    // 方法
    setToken,
    register,
    login,
    logout,
    fetchCurrentUser,
    initAuth
  }
})
