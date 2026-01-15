/**
 * usePolling composable 单元测试
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { usePolling } from '@/composables/usePolling'

// Mock Vue lifecycle hooks
vi.mock('vue', async () => {
  const actual = await vi.importActual('vue')
  return {
    ...actual,
    onMounted: vi.fn((cb) => cb()),
    onUnmounted: vi.fn()
  }
})

describe('usePolling', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    // Mock document.hidden
    Object.defineProperty(document, 'hidden', {
      configurable: true,
      get: () => false
    })
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.clearAllMocks()
  })

  describe('基本功能', () => {
    it('应该正确初始化状态', () => {
      const callback = vi.fn()
      const { isPolling, isPaused } = usePolling(callback)

      expect(isPolling.value).toBe(false)
      expect(isPaused.value).toBe(false)
    })

    it('start 应该开始轮询', () => {
      const callback = vi.fn()
      const { start, isPolling } = usePolling(callback, { interval: 1000 })

      start()

      expect(isPolling.value).toBe(true)
    })

    it('stop 应该停止轮询', () => {
      const callback = vi.fn()
      const { start, stop, isPolling } = usePolling(callback, { interval: 1000 })

      start()
      stop()

      expect(isPolling.value).toBe(false)
    })

    it('应该按指定间隔执行回调', () => {
      const callback = vi.fn()
      const { start } = usePolling(callback, { interval: 1000 })

      start()

      // 初始不执行
      expect(callback).not.toHaveBeenCalled()

      // 1秒后执行
      vi.advanceTimersByTime(1000)
      expect(callback).toHaveBeenCalledTimes(1)

      // 2秒后再次执行
      vi.advanceTimersByTime(1000)
      expect(callback).toHaveBeenCalledTimes(2)
    })

    it('immediate 选项应该立即执行一次', () => {
      const callback = vi.fn()
      const { start } = usePolling(callback, { interval: 1000, immediate: true })

      start()

      expect(callback).toHaveBeenCalledTimes(1)
    })

    it('stop 后不应该继续执行回调', () => {
      const callback = vi.fn()
      const { start, stop } = usePolling(callback, { interval: 1000 })

      start()
      vi.advanceTimersByTime(1000)
      expect(callback).toHaveBeenCalledTimes(1)

      stop()
      vi.advanceTimersByTime(5000)
      expect(callback).toHaveBeenCalledTimes(1)
    })

    it('多次调用 start 不应该创建多个定时器', () => {
      const callback = vi.fn()
      const { start } = usePolling(callback, { interval: 1000 })

      start()
      start()
      start()

      vi.advanceTimersByTime(1000)
      expect(callback).toHaveBeenCalledTimes(1)
    })
  })

  describe('页面可见性', () => {
    it('页面不可见时应该暂停轮询', () => {
      const callback = vi.fn()
      const { start, isPaused } = usePolling(callback, { interval: 1000, pauseOnHidden: true })

      start()
      vi.advanceTimersByTime(1000)
      expect(callback).toHaveBeenCalledTimes(1)

      // 模拟页面不可见
      Object.defineProperty(document, 'hidden', {
        configurable: true,
        get: () => true
      })
      document.dispatchEvent(new Event('visibilitychange'))

      expect(isPaused.value).toBe(true)

      // 暂停后不应该执行
      vi.advanceTimersByTime(5000)
      expect(callback).toHaveBeenCalledTimes(1)
    })

    it('页面恢复可见时应该立即执行一次并恢复轮询', () => {
      const callback = vi.fn()
      const { start, isPaused } = usePolling(callback, { interval: 1000, pauseOnHidden: true })

      start()

      // 模拟页面不可见
      Object.defineProperty(document, 'hidden', {
        configurable: true,
        get: () => true
      })
      document.dispatchEvent(new Event('visibilitychange'))

      // 模拟页面恢复可见
      Object.defineProperty(document, 'hidden', {
        configurable: true,
        get: () => false
      })
      document.dispatchEvent(new Event('visibilitychange'))

      expect(isPaused.value).toBe(false)
      // 恢复可见时立即执行一次
      expect(callback).toHaveBeenCalledTimes(1)
    })

    it('pauseOnHidden 为 false 时不应该暂停', () => {
      const callback = vi.fn()
      const { start, isPaused } = usePolling(callback, { interval: 1000, pauseOnHidden: false })

      start()

      // 模拟页面不可见
      Object.defineProperty(document, 'hidden', {
        configurable: true,
        get: () => true
      })
      document.dispatchEvent(new Event('visibilitychange'))

      expect(isPaused.value).toBe(false)

      vi.advanceTimersByTime(1000)
      expect(callback).toHaveBeenCalledTimes(1)
    })
  })

  describe('refresh 方法', () => {
    it('refresh 应该手动触发一次回调', () => {
      const callback = vi.fn()
      const { refresh } = usePolling(callback, { interval: 1000 })

      refresh()

      expect(callback).toHaveBeenCalledTimes(1)
    })

    it('refresh 不应该影响定时器', () => {
      const callback = vi.fn()
      const { start, refresh } = usePolling(callback, { interval: 1000 })

      start()
      refresh()
      expect(callback).toHaveBeenCalledTimes(1)

      vi.advanceTimersByTime(1000)
      expect(callback).toHaveBeenCalledTimes(2)
    })
  })

  describe('默认值', () => {
    it('默认间隔应该是 5000ms', () => {
      const callback = vi.fn()
      const { start } = usePolling(callback)

      start()

      vi.advanceTimersByTime(4999)
      expect(callback).not.toHaveBeenCalled()

      vi.advanceTimersByTime(1)
      expect(callback).toHaveBeenCalledTimes(1)
    })

    it('默认 immediate 应该是 false', () => {
      const callback = vi.fn()
      const { start } = usePolling(callback)

      start()

      expect(callback).not.toHaveBeenCalled()
    })

    it('默认 pauseOnHidden 应该是 true', () => {
      const callback = vi.fn()
      const { start, isPaused } = usePolling(callback)

      start()

      // 模拟页面不可见
      Object.defineProperty(document, 'hidden', {
        configurable: true,
        get: () => true
      })
      document.dispatchEvent(new Event('visibilitychange'))

      expect(isPaused.value).toBe(true)
    })
  })

  describe('异步回调', () => {
    it('应该支持异步回调', async () => {
      const callback = vi.fn().mockResolvedValue(undefined)
      const { start } = usePolling(callback, { interval: 1000 })

      start()
      vi.advanceTimersByTime(1000)

      expect(callback).toHaveBeenCalledTimes(1)
    })
  })

  describe('边界情况', () => {
    it('页面初始不可见时 start 不应该启动定时器', () => {
      Object.defineProperty(document, 'hidden', {
        configurable: true,
        get: () => true
      })

      const callback = vi.fn()
      const { start, isPaused, isPolling } = usePolling(callback, { interval: 1000, pauseOnHidden: true })

      start()

      expect(isPolling.value).toBe(true)
      expect(isPaused.value).toBe(true)

      vi.advanceTimersByTime(5000)
      expect(callback).not.toHaveBeenCalled()
    })

    it('未启动轮询时页面可见性变化不应该触发回调', () => {
      const callback = vi.fn()
      usePolling(callback, { interval: 1000, pauseOnHidden: true })

      // 模拟页面不可见再恢复
      Object.defineProperty(document, 'hidden', {
        configurable: true,
        get: () => true
      })
      document.dispatchEvent(new Event('visibilitychange'))

      Object.defineProperty(document, 'hidden', {
        configurable: true,
        get: () => false
      })
      document.dispatchEvent(new Event('visibilitychange'))

      expect(callback).not.toHaveBeenCalled()
    })
  })
})
