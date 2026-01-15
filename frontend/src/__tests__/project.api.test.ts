/**
 * project API 单元测试
 * 重点测试筛选参数的序列化
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { getProject, getProjects, createProject, updateProject, deleteProject } from '@/api/project'
import * as request from '@/api/request'
import type { Project, ProjectDetail, TaskFilterParams } from '@/types'

vi.mock('@/api/request')

const mockProject: Project = {
  id: 1,
  name: '测试项目',
  description: null,
  owner_id: 1,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
}

const mockProjectDetail: ProjectDetail = {
  ...mockProject,
  columns: []
}

describe('project API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getProject', () => {
    it('无筛选参数时应该调用正确的 URL', async () => {
      vi.mocked(request.get).mockResolvedValue(mockProjectDetail)

      await getProject(1)

      expect(request.get).toHaveBeenCalledWith('/projects/1')
    })

    it('有 keyword 筛选参数时应该正确序列化', async () => {
      vi.mocked(request.get).mockResolvedValue(mockProjectDetail)

      const filter: TaskFilterParams = { keyword: '测试' }
      await getProject(1, filter)

      expect(request.get).toHaveBeenCalledWith('/projects/1?keyword=%E6%B5%8B%E8%AF%95')
    })

    it('有 assignee_id 筛选参数时应该正确序列化', async () => {
      vi.mocked(request.get).mockResolvedValue(mockProjectDetail)

      const filter: TaskFilterParams = { assignee_id: 123 }
      await getProject(1, filter)

      expect(request.get).toHaveBeenCalledWith('/projects/1?assignee_id=123')
    })

    it('有 priority 筛选参数时应该正确序列化', async () => {
      vi.mocked(request.get).mockResolvedValue(mockProjectDetail)

      const filter: TaskFilterParams = { priority: 'high' }
      await getProject(1, filter)

      expect(request.get).toHaveBeenCalledWith('/projects/1?priority=high')
    })

    it('有 due_date_start 筛选参数时应该正确序列化', async () => {
      vi.mocked(request.get).mockResolvedValue(mockProjectDetail)

      const filter: TaskFilterParams = { due_date_start: '2025-01-01' }
      await getProject(1, filter)

      expect(request.get).toHaveBeenCalledWith('/projects/1?due_date_start=2025-01-01')
    })

    it('有 due_date_end 筛选参数时应该正确序列化', async () => {
      vi.mocked(request.get).mockResolvedValue(mockProjectDetail)

      const filter: TaskFilterParams = { due_date_end: '2025-12-31' }
      await getProject(1, filter)

      expect(request.get).toHaveBeenCalledWith('/projects/1?due_date_end=2025-12-31')
    })

    it('多个筛选参数时应该正确组合', async () => {
      vi.mocked(request.get).mockResolvedValue(mockProjectDetail)

      const filter: TaskFilterParams = {
        keyword: '测试',
        priority: 'high',
        assignee_id: 1
      }
      await getProject(1, filter)

      const call = vi.mocked(request.get).mock.calls[0][0]
      expect(call).toContain('/projects/1?')
      expect(call).toContain('keyword=')
      expect(call).toContain('priority=high')
      expect(call).toContain('assignee_id=1')
    })

    it('空筛选对象时不应该添加查询参数', async () => {
      vi.mocked(request.get).mockResolvedValue(mockProjectDetail)

      await getProject(1, {})

      expect(request.get).toHaveBeenCalledWith('/projects/1')
    })

    it('assignee_id 为 0 时应该正确序列化', async () => {
      vi.mocked(request.get).mockResolvedValue(mockProjectDetail)

      const filter: TaskFilterParams = { assignee_id: 0 }
      await getProject(1, filter)

      expect(request.get).toHaveBeenCalledWith('/projects/1?assignee_id=0')
    })

    it('assignee_id 为 null 时不应该添加参数', async () => {
      vi.mocked(request.get).mockResolvedValue(mockProjectDetail)

      const filter: TaskFilterParams = { assignee_id: undefined }
      await getProject(1, filter)

      expect(request.get).toHaveBeenCalledWith('/projects/1')
    })
  })

  describe('getProjects', () => {
    it('应该调用正确的 API 端点', async () => {
      vi.mocked(request.get).mockResolvedValue([mockProject])

      const result = await getProjects()

      expect(request.get).toHaveBeenCalledWith('/projects')
      expect(result).toEqual([mockProject])
    })
  })

  describe('createProject', () => {
    it('应该调用正确的 API 端点', async () => {
      vi.mocked(request.post).mockResolvedValue(mockProject)

      const result = await createProject({ name: '新项目' })

      expect(request.post).toHaveBeenCalledWith('/projects', { name: '新项目' })
      expect(result).toEqual(mockProject)
    })
  })

  describe('updateProject', () => {
    it('应该调用正确的 API 端点', async () => {
      const updatedProject = { ...mockProject, name: '更新后的项目' }
      vi.mocked(request.put).mockResolvedValue(updatedProject)

      const result = await updateProject(1, { name: '更新后的项目' })

      expect(request.put).toHaveBeenCalledWith('/projects/1', { name: '更新后的项目' })
      expect(result.name).toBe('更新后的项目')
    })
  })

  describe('deleteProject', () => {
    it('应该调用正确的 API 端点', async () => {
      vi.mocked(request.del).mockResolvedValue(undefined)

      await deleteProject(1)

      expect(request.del).toHaveBeenCalledWith('/projects/1')
    })
  })
})
