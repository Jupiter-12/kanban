/**
 * 评论 API 单元测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import * as commentApi from '@/api/comment'
import { get, post, del } from '@/api/request'
import type { Comment } from '@/types'

// Mock request 模块
vi.mock('@/api/request', () => ({
  get: vi.fn(),
  post: vi.fn(),
  del: vi.fn()
}))

// 测试数据工厂
function createComment(overrides: Partial<Comment> = {}): Comment {
  return {
    id: 1,
    task_id: 1,
    user_id: 1,
    content: '测试评论',
    created_at: '2024-01-01T00:00:00Z',
    user: {
      id: 1,
      username: 'testuser',
      display_name: '测试用户'
    },
    ...overrides
  }
}

describe('comment API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getComments', () => {
    it('应该正确调用 GET 请求获取评论列表', async () => {
      const mockComments = [
        createComment({ id: 1, content: '评论1' }),
        createComment({ id: 2, content: '评论2' })
      ]
      vi.mocked(get).mockResolvedValue(mockComments)

      const result = await commentApi.getComments(1)

      expect(get).toHaveBeenCalledWith('/tasks/1/comments')
      expect(result).toEqual(mockComments)
    })

    it('应该正确处理空评论列表', async () => {
      vi.mocked(get).mockResolvedValue([])

      const result = await commentApi.getComments(1)

      expect(result).toEqual([])
    })
  })

  describe('createComment', () => {
    it('应该正确调用 POST 请求创建评论', async () => {
      const mockComment = createComment({ content: '新评论' })
      vi.mocked(post).mockResolvedValue(mockComment)

      const result = await commentApi.createComment(1, { content: '新评论' })

      expect(post).toHaveBeenCalledWith('/tasks/1/comments', { content: '新评论' })
      expect(result).toEqual(mockComment)
    })
  })

  describe('deleteComment', () => {
    it('应该正确调用 DELETE 请求删除评论', async () => {
      vi.mocked(del).mockResolvedValue(undefined)

      await commentApi.deleteComment(1)

      expect(del).toHaveBeenCalledWith('/comments/1')
    })
  })
})
