/**
 * 轮询刷新 composable
 * 支持页面可见性检测，不可见时暂停轮询
 */
import { ref, onMounted, onUnmounted } from 'vue'

export interface UsePollingOptions {
  /** 轮询间隔（毫秒），默认 5000 */
  interval?: number
  /** 是否立即执行一次，默认 false */
  immediate?: boolean
  /** 是否在页面不可见时暂停轮询，默认 true */
  pauseOnHidden?: boolean
}

export function usePolling(
  callback: () => void | Promise<void>,
  options: UsePollingOptions = {}
) {
  const { interval = 5000, immediate = false, pauseOnHidden = true } = options

  const isPolling = ref(false)
  const isPaused = ref(false)
  let timerId: ReturnType<typeof setInterval> | null = null

  /**
   * 处理页面可见性变化
   */
  function handleVisibilityChange() {
    if (!pauseOnHidden) return

    if (document.hidden) {
      // 页面不可见，暂停轮询
      isPaused.value = true
      stopTimer()
    } else {
      // 页面可见，恢复轮询
      isPaused.value = false
      if (isPolling.value) {
        // 立即执行一次刷新，然后恢复定时器
        callback()
        startTimer()
      }
    }
  }

  /**
   * 启动定时器
   */
  function startTimer() {
    if (timerId) return
    timerId = setInterval(() => {
      if (!isPaused.value) {
        callback()
      }
    }, interval)
  }

  /**
   * 停止定时器
   */
  function stopTimer() {
    if (timerId) {
      clearInterval(timerId)
      timerId = null
    }
  }

  /**
   * 开始轮询
   */
  function start() {
    if (isPolling.value) return
    isPolling.value = true
    isPaused.value = document.hidden && pauseOnHidden

    if (immediate && !isPaused.value) {
      callback()
    }

    if (!isPaused.value) {
      startTimer()
    }
  }

  /**
   * 停止轮询
   */
  function stop() {
    isPolling.value = false
    isPaused.value = false
    stopTimer()
  }

  /**
   * 手动触发一次刷新
   */
  function refresh() {
    callback()
  }

  // 监听页面可见性变化
  onMounted(() => {
    if (pauseOnHidden) {
      document.addEventListener('visibilitychange', handleVisibilityChange)
    }
  })

  onUnmounted(() => {
    stop()
    if (pauseOnHidden) {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  })

  return {
    /** 是否正在轮询 */
    isPolling,
    /** 是否已暂停（页面不可见） */
    isPaused,
    /** 开始轮询 */
    start,
    /** 停止轮询 */
    stop,
    /** 手动刷新 */
    refresh
  }
}
