/**
 * HTTP客户端配置
 */
import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

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
    // 可在此添加认证token
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
