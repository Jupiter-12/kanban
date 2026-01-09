/**
 * task API 单元测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { moveTask, createTask, updateTask, deleteTask } from '@/api/task'
import * as request from '@/api/request'
import type { Task, TaskMoveRequest, TaskCreateRequest, TaskUpdateRequest } from '@/types'

vi.mock('@/api/request')

const mockTask: Task = {
  id: 1,
  title: '测试任务',
  column_id: 1,
  position: 0,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
}

describe('task API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('moveTask', () => {
    it('应该调用正确的 API 端点和参数', async () => {
      vi.mocked(request.put).mockResolvedValue(mockTask)
      
      const moveData: TaskMoveRequest = {
        target_column_id: 2,
        position: 1
      }
      
      const result = await moveTask(1, moveData)
      
      expect(request.put).toHaveBeenCalledWith('/tasks/1/move', moveData)
      expect(result).toEqual(mockTask)
    })

    it('应该正确处理列内移动', async () => {
      const movedTask = { ...mockTask, position: 2 }
      vi.mocked(request.put).mockResolvedValue(movedTask)
      
      const moveData: TaskMoveRequest = {
        target_column_id: 1,
        position: 2
      }
      
      const result = await moveTask(1, moveData)
      
      expect(request.put).toHaveBeenCalledWith('/tasks/1/move', moveData)
      expect(result.position).toBe(2)
    })

    it('应该正确处理跨列移动', async () => {
      const movedTask = { ...mockTask, column_id: 2, position: 0 }
      vi.mocked(request.put).mockResolvedValue(movedTask)
      
      const moveData: TaskMoveRequest = {
        target_column_id: 2,
        position: 0
      }
      
      const result = await moveTask(1, moveData)
      
      expect(result.column_id).toBe(2)
      expect(result.position).toBe(0)
    })

    it('当 API 失败时应该抛出错误', async () => {
      vi.mocked(request.put).mockRejectedValue(new Error('网络错误'))
      
      const moveData: TaskMoveRequest = {
        target_column_id: 2,
        position: 0
      }
      
      await expect(moveTask(1, moveData)).rejects.toThrow('网络错误')
    })
  })

  describe('createTask', () => {
    it('应该调用正确的 API 端点', async () => {
      vi.mocked(request.post).mockResolvedValue(mockTask)
      
      const createData: TaskCreateRequest = { title: '新任务' }
      
      const result = await createTask(1, createData)
      
      expect(request.post).toHaveBeenCalledWith('/columns/1/tasks', createData)
      expect(result).toEqual(mockTask)
    })
  })

  describe('updateTask', () => {
    it('应该调用正确的 API 端点', async () => {
      const updatedTask = { ...mockTask, title: '更新后的任务' }
      vi.mocked(request.put).mockResolvedValue(updatedTask)
      
      const updateData: TaskUpdateRequest = { title: '更新后的任务' }
      
      const result = await updateTask(1, updateData)
      
      expect(request.put).toHaveBeenCalledWith('/tasks/1', updateData)
      expect(result.title).toBe('更新后的任务')
    })
  })

  describe('deleteTask', () => {
    it('应该调用正确的 API 端点', async () => {
      vi.mocked(request.del).mockResolvedValue(undefined)
      
      await deleteTask(1)
      
      expect(request.del).toHaveBeenCalledWith('/tasks/1')
    })
  })
})
