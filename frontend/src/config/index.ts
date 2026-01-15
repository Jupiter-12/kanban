/**
 * 应用配置
 */

/** 轮询刷新间隔（毫秒） */
export const POLLING_INTERVAL = import.meta.env.VITE_POLLING_INTERVAL
  ? Number(import.meta.env.VITE_POLLING_INTERVAL)
  : 5000
