/**
 * column API 单元测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { reorderColumns, createColumn, updateColumn, deleteColumn } from '@/api/column'
import * as request from '@/api/request'
import type { Column, ColumnReorderRequest, ColumnCreateRequest, ColumnUpdateRequest } from '@/types'

vi.mock('@/api/request')

const mockColumn: Column = {
  id: 1,
  name: '测试列',
  project_id: 1,
  position: 0,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
}

describe('column API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('reorderColumns', () => {
    it('应该调用正确的 API 端点和参数', async () => {
      const reorderedColumns = [
        { ...mockColumn, id: 2, position: 0 },
        { ...mockColumn, id: 1, position: 1 },
        { ...mockColumn, id: 3, position: 2 }
      ]
      vi.mocked(request.put).mockResolvedValue(reorderedColumns)
      
      const reorderData: ColumnReorderRequest = {
        column_ids: [2, 1, 3]
      }
      
      const result = await reorderColumns(reorderData)
      
      expect(request.put).toHaveBeenCalledWith('/columns/reorder', reorderData)
      expect(result).toEqual(reorderedColumns)
    })

    it('当 API 失败时应该抛出错误', async () => {
      vi.mocked(request.put).mockRejectedValue(new Error('网络错误'))
      
      const reorderData: ColumnReorderRequest = {
        column_ids: [1, 2, 3]
      }
      
      await expect(reorderColumns(reorderData)).rejects.toThrow('网络错误')
    })

    it('应该正确处理空列表', async () => {
      vi.mocked(request.put).mockResolvedValue([])
      
      const reorderData: ColumnReorderRequest = {
        column_ids: []
      }
      
      const result = await reorderColumns(reorderData)
      
      expect(request.put).toHaveBeenCalledWith('/columns/reorder', reorderData)
      expect(result).toEqual([])
    })
  })

  describe('createColumn', () => {
    it('应该调用正确的 API 端点', async () => {
      vi.mocked(request.post).mockResolvedValue(mockColumn)
      
      const createData: ColumnCreateRequest = { name: '新列' }
      
      const result = await createColumn(1, createData)
      
      expect(request.post).toHaveBeenCalledWith('/projects/1/columns', createData)
      expect(result).toEqual(mockColumn)
    })
  })

  describe('updateColumn', () => {
    it('应该调用正确的 API 端点', async () => {
      const updatedColumn = { ...mockColumn, name: '更新后的列' }
      vi.mocked(request.put).mockResolvedValue(updatedColumn)
      
      const updateData: ColumnUpdateRequest = { name: '更新后的列' }
      
      const result = await updateColumn(1, updateData)
      
      expect(request.put).toHaveBeenCalledWith('/columns/1', updateData)
      expect(result.name).toBe('更新后的列')
    })
  })

  describe('deleteColumn', () => {
    it('应该调用正确的 API 端点', async () => {
      vi.mocked(request.del).mockResolvedValue(undefined)
      
      await deleteColumn(1)
      
      expect(request.del).toHaveBeenCalledWith('/columns/1')
    })
  })
})
