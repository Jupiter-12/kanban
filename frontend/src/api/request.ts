/**
 * HTTP客户端配置
 */
import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

/** Token存储键名 */
const TOKEN_KEY = 'kanban_token'

/** 不需要处理401跳转的接口路径 */
const AUTH_WHITELIST = ['/auth/login', '/auth/register']

const instance: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 请求拦截器
 */
instance.interceptors.request.use(
  (config) => {
    // 自动携带Token
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 */
instance.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error) => {
    // 统一错误处理
    if (error.response) {
      const { status, data, config } = error.response
      const message = data?.detail || '请求失败'
      const requestUrl = config?.url || ''

      // 检查是否是认证相关接口
      const isAuthEndpoint = AUTH_WHITELIST.some(path => requestUrl.includes(path))

      if (status === 401 && !isAuthEndpoint) {
        // 未认证，清除Token并跳转登录（排除登录/注册接口）
        localStorage.removeItem(TOKEN_KEY)
        ElMessage.error('登录已过期，请重新登录')
        // 跳转到登录页
        window.location.href = '/login'
      } else if (status === 401 && isAuthEndpoint) {
        // 登录/注册接口的401，显示具体错误信息
        ElMessage.error(message)
      } else if (status === 403) {
        ElMessage.error('没有权限执行此操作')
      } else if (status === 429) {
        // 请求过于频繁（速率限制）
        ElMessage.warning(message)
      } else if (status === 400) {
        ElMessage.error(message)
      } else if (status >= 500) {
        ElMessage.error('服务器错误，请稍后重试')
      } else {
        ElMessage.error(message)
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error('请求配置错误')
    }
    return Promise.reject(error)
  }
)

/**
 * 封装GET请求
 * @param url - 请求地址
 * @param config - 请求配置
 */
export function get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return instance.get(url, config)
}

/**
 * 封装POST请求
 * @param url - 请求地址
 * @param data - 请求数据
 * @param config - 请求配置
 */
export function post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  return instance.post(url, data, config)
}

/**
 * 封装PUT请求
 * @param url - 请求地址
 * @param data - 请求数据
 * @param config - 请求配置
 */
export function put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  return instance.put(url, data, config)
}

/**
 * 封装DELETE请求
 * @param url - 请求地址
 * @param config - 请求配置
 */
export function del<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return instance.delete(url, config)
}

export default instance
