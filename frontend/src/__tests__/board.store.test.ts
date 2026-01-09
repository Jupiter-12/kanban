/**
 * board store 单元测试
 * 重点测试拖拽排序相关功能
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useBoardStore } from '@/stores/board'
import * as taskApi from '@/api/task'
import * as columnApi from '@/api/column'
import * as projectApi from '@/api/project'
import type { ProjectDetail, Task, ColumnWithTasks } from '@/types'

// Mock API 模块
vi.mock('@/api/task')
vi.mock('@/api/column')
vi.mock('@/api/project')

// 测试数据工厂
function createTask(overrides: Partial<Task> = {}): Task {
  return {
    id: 1,
    title: '测试任务',
    column_id: 1,
    position: 0,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    ...overrides
  }
}

function createColumn(overrides: Partial<ColumnWithTasks> = {}): ColumnWithTasks {
  return {
    id: 1,
    name: '测试列',
    project_id: 1,
    position: 0,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    tasks: [],
    ...overrides
  }
}

function createProject(overrides: Partial<ProjectDetail> = {}): ProjectDetail {
  return {
    id: 1,
    name: '测试项目',
    description: null,
    owner_id: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    columns: [],
    ...overrides
  }
}

describe('useBoardStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('moveTask - 列内移动', () => {
    it('应该正确更新任务位置', async () => {
      const store = useBoardStore()
      const task1 = createTask({ id: 1, position: 0 })
      const task2 = createTask({ id: 2, position: 1 })
      const task3 = createTask({ id: 3, position: 2 })
      
      // 模拟 vuedraggable 已经移动了数组：task1 从位置0移动到位置2
      // 移动后数组顺序：[task2, task3, task1]
      const column = createColumn({
        id: 1,
        tasks: [task2, task3, task1]
      })
      
      store.currentProject = createProject({ columns: [column] })
      
      const updatedTask = createTask({ id: 1, position: 2 })
      vi.mocked(taskApi.moveTask).mockResolvedValue(updatedTask)
      
      await store.moveTask(1, 1, 1, 2)
      
      expect(taskApi.moveTask).toHaveBeenCalledWith(1, {
        target_column_id: 1,
        position: 2
      })
      
      // 验证所有任务的 position 已更新
      expect(column.tasks[0].position).toBe(0)
      expect(column.tasks[1].position).toBe(1)
      expect(column.tasks[2].position).toBe(2)
    })

    it('当后端失败时应该重新加载项目数据', async () => {
      const store = useBoardStore()
      const task = createTask({ id: 1 })
      const column = createColumn({ id: 1, tasks: [task] })
      
      store.currentProject = createProject({ id: 1, columns: [column] })
      
      vi.mocked(taskApi.moveTask).mockRejectedValue(new Error('网络错误'))
      vi.mocked(projectApi.getProject).mockResolvedValue(createProject({ id: 1 }))
      
      await expect(store.moveTask(1, 1, 1, 0)).rejects.toThrow('网络错误')
      
      expect(projectApi.getProject).toHaveBeenCalledWith(1)
    })
  })

  describe('moveTask - 跨列移动', () => {
    it('应该正确更新源列和目标列的任务位置', async () => {
      const store = useBoardStore()
      
      // 源列原有任务
      const sourceTask1 = createTask({ id: 1, column_id: 1, position: 0 })
      const sourceTask2 = createTask({ id: 2, column_id: 1, position: 1 })
      
      // 目标列原有任务
      const targetTask1 = createTask({ id: 3, column_id: 2, position: 0 })
      
      // 模拟 vuedraggable 已经将 sourceTask1 移动到目标列
      // 源列：[sourceTask2]
      // 目标列：[targetTask1, sourceTask1]（sourceTask1 被插入到位置1）
      const sourceColumn = createColumn({
        id: 1,
        tasks: [sourceTask2]
      })
      
      const targetColumn = createColumn({
        id: 2,
        tasks: [targetTask1, sourceTask1]
      })
      
      store.currentProject = createProject({
        columns: [sourceColumn, targetColumn]
      })
      
      const updatedTask = createTask({ id: 1, column_id: 2, position: 1 })
      vi.mocked(taskApi.moveTask).mockResolvedValue(updatedTask)
      
      await store.moveTask(1, 1, 2, 1)
      
      expect(taskApi.moveTask).toHaveBeenCalledWith(1, {
        target_column_id: 2,
        position: 1
      })
      
      // 验证源列任务位置更新
      expect(sourceColumn.tasks[0].position).toBe(0)
      
      // 验证目标列任务位置更新
      expect(targetColumn.tasks[0].position).toBe(0)
      expect(targetColumn.tasks[1].position).toBe(1)
      
      // 验证任务的 column_id 已更新
      expect(targetColumn.tasks[1].column_id).toBe(2)
    })

    it('当目标列不存在时应该直接返回', async () => {
      const store = useBoardStore()
      const task = createTask({ id: 1, column_id: 1 })
      const column = createColumn({ id: 1, tasks: [task] })
      
      store.currentProject = createProject({ columns: [column] })
      
      await store.moveTask(1, 1, 999, 0)
      
      expect(taskApi.moveTask).not.toHaveBeenCalled()
    })

    it('当任务在目标列中不存在时应该直接返回', async () => {
      const store = useBoardStore()
      const column = createColumn({ id: 1, tasks: [] })
      
      store.currentProject = createProject({ columns: [column] })
      
      await store.moveTask(999, 1, 1, 0)
      
      expect(taskApi.moveTask).not.toHaveBeenCalled()
    })
  })

  describe('reorderColumns - 列排序', () => {
    it('应该正确更新列的位置', async () => {
      const store = useBoardStore()
      
      // 模拟 vuedraggable 已经重新排序了列数组
      // 原顺序：[col1, col2, col3] -> 新顺序：[col2, col1, col3]
      const col1 = createColumn({ id: 1, position: 0 })
      const col2 = createColumn({ id: 2, position: 1 })
      const col3 = createColumn({ id: 3, position: 2 })
      
      store.currentProject = createProject({
        columns: [col2, col1, col3]
      })
      
      vi.mocked(columnApi.reorderColumns).mockResolvedValue([])
      
      await store.reorderColumns([2, 1, 3])
      
      expect(columnApi.reorderColumns).toHaveBeenCalledWith({
        column_ids: [2, 1, 3]
      })
      
      // 验证列的 position 已按数组索引更新
      expect(col2.position).toBe(0)
      expect(col1.position).toBe(1)
      expect(col3.position).toBe(2)
    })

    it('当后端失败时应该重新加载项目数据', async () => {
      const store = useBoardStore()
      const column = createColumn({ id: 1 })
      
      store.currentProject = createProject({ id: 1, columns: [column] })
      
      vi.mocked(columnApi.reorderColumns).mockRejectedValue(new Error('网络错误'))
      vi.mocked(projectApi.getProject).mockResolvedValue(createProject({ id: 1 }))
      
      await expect(store.reorderColumns([1])).rejects.toThrow('网络错误')
      
      expect(projectApi.getProject).toHaveBeenCalledWith(1)
    })
  })

  describe('边界情况', () => {
    it('当 currentProject 为 null 时 moveTask 应该直接返回', async () => {
      const store = useBoardStore()
      store.currentProject = null
      
      await store.moveTask(1, 1, 1, 0)
      
      expect(taskApi.moveTask).not.toHaveBeenCalled()
    })

    it('当 currentProject 为 null 时 reorderColumns 应该直接返回', async () => {
      const store = useBoardStore()
      store.currentProject = null
      
      await store.reorderColumns([1, 2, 3])
      
      expect(columnApi.reorderColumns).not.toHaveBeenCalled()
    })

    it('移动任务到空列应该正常工作', async () => {
      const store = useBoardStore()
      const task = createTask({ id: 1, column_id: 1 })
      
      // 模拟 vuedraggable 已经将任务移动到空的目标列
      const sourceColumn = createColumn({ id: 1, tasks: [] })
      const targetColumn = createColumn({ id: 2, tasks: [task] })
      
      store.currentProject = createProject({
        columns: [sourceColumn, targetColumn]
      })
      
      const updatedTask = createTask({ id: 1, column_id: 2, position: 0 })
      vi.mocked(taskApi.moveTask).mockResolvedValue(updatedTask)
      
      await store.moveTask(1, 1, 2, 0)
      
      expect(taskApi.moveTask).toHaveBeenCalledWith(1, {
        target_column_id: 2,
        position: 0
      })
    })
  })

  describe('getColumnById', () => {
    it('应该返回正确的列', () => {
      const store = useBoardStore()
      const column = createColumn({ id: 1, name: '待办' })
      
      store.currentProject = createProject({ columns: [column] })
      
      expect(store.getColumnById(1)).toEqual(column)
    })

    it('当列不存在时应该返回 undefined', () => {
      const store = useBoardStore()
      store.currentProject = createProject({ columns: [] })
      
      expect(store.getColumnById(999)).toBeUndefined()
    })
  })

  describe('getTaskById', () => {
    it('应该返回正确的任务', () => {
      const store = useBoardStore()
      const task = createTask({ id: 1, title: '测试任务' })
      const column = createColumn({ id: 1, tasks: [task] })
      
      store.currentProject = createProject({ columns: [column] })
      
      expect(store.getTaskById(1)).toEqual(task)
    })

    it('当任务不存在时应该返回 undefined', () => {
      const store = useBoardStore()
      const column = createColumn({ id: 1, tasks: [] })
      
      store.currentProject = createProject({ columns: [column] })
      
      expect(store.getTaskById(999)).toBeUndefined()
    })

    it('当 currentProject 为 null 时应该返回 undefined', () => {
      const store = useBoardStore()
      store.currentProject = null
      
      expect(store.getTaskById(1)).toBeUndefined()
    })
  })

  describe('updateTask', () => {
    it('应该正确更新任务', async () => {
      const store = useBoardStore()
      const task = createTask({ id: 1, title: '原标题' })
      const column = createColumn({ id: 1, tasks: [task] })
      
      store.currentProject = createProject({ columns: [column] })
      
      const updatedTask = createTask({ id: 1, title: '新标题' })
      vi.mocked(taskApi.updateTask).mockResolvedValue(updatedTask)
      
      await store.updateTask(1, { title: '新标题' })
      
      expect(taskApi.updateTask).toHaveBeenCalledWith(1, { title: '新标题' })
      expect(column.tasks[0].title).toBe('新标题')
    })

    it('当 currentProject 为 null 时应该直接返回', async () => {
      const store = useBoardStore()
      store.currentProject = null
      
      await store.updateTask(1, { title: '新标题' })
      
      expect(taskApi.updateTask).not.toHaveBeenCalled()
    })

    it('当任务不存在时不应该更新', async () => {
      const store = useBoardStore()
      const column = createColumn({ id: 1, tasks: [] })
      
      store.currentProject = createProject({ columns: [column] })
      
      const updatedTask = createTask({ id: 999, title: '新标题' })
      vi.mocked(taskApi.updateTask).mockResolvedValue(updatedTask)
      
      await store.updateTask(999, { title: '新标题' })
      
      expect(taskApi.updateTask).toHaveBeenCalled()
      // 任务不在任何列中，所以不会更新本地状态
    })
  })

  describe('deleteTask', () => {
    it('应该正确删除任务', async () => {
      const store = useBoardStore()
      const task1 = createTask({ id: 1 })
      const task2 = createTask({ id: 2 })
      const column = createColumn({ id: 1, tasks: [task1, task2] })
      
      store.currentProject = createProject({ columns: [column] })
      
      vi.mocked(taskApi.deleteTask).mockResolvedValue(undefined)
      
      await store.deleteTask(1)
      
      expect(taskApi.deleteTask).toHaveBeenCalledWith(1)
      expect(column.tasks).toHaveLength(1)
      expect(column.tasks[0].id).toBe(2)
    })

    it('当 currentProject 为 null 时应该直接返回', async () => {
      const store = useBoardStore()
      store.currentProject = null
      
      await store.deleteTask(1)
      
      expect(taskApi.deleteTask).not.toHaveBeenCalled()
    })

    it('当任务不存在时不应该修改列表', async () => {
      const store = useBoardStore()
      const task = createTask({ id: 1 })
      const column = createColumn({ id: 1, tasks: [task] })
      
      store.currentProject = createProject({ columns: [column] })
      
      vi.mocked(taskApi.deleteTask).mockResolvedValue(undefined)
      
      await store.deleteTask(999)
      
      expect(taskApi.deleteTask).toHaveBeenCalledWith(999)
      expect(column.tasks).toHaveLength(1)
    })
  })

  describe('createTask', () => {
    it('应该正确创建任务', async () => {
      const store = useBoardStore()
      const column = createColumn({ id: 1, tasks: [] })
      
      store.currentProject = createProject({ columns: [column] })
      
      const newTask = createTask({ id: 1, title: '新任务', column_id: 1 })
      vi.mocked(taskApi.createTask).mockResolvedValue(newTask)
      
      await store.createTask(1, { title: '新任务' })
      
      expect(taskApi.createTask).toHaveBeenCalledWith(1, { title: '新任务' })
      expect(column.tasks).toHaveLength(1)
      expect(column.tasks[0].title).toBe('新任务')
    })

    it('当 currentProject 为 null 时应该直接返回', async () => {
      const store = useBoardStore()
      store.currentProject = null
      
      await store.createTask(1, { title: '新任务' })
      
      expect(taskApi.createTask).not.toHaveBeenCalled()
    })

    it('当列不存在时不应该添加任务', async () => {
      const store = useBoardStore()
      const column = createColumn({ id: 1, tasks: [] })
      
      store.currentProject = createProject({ columns: [column] })
      
      const newTask = createTask({ id: 1, title: '新任务', column_id: 999 })
      vi.mocked(taskApi.createTask).mockResolvedValue(newTask)
      
      await store.createTask(999, { title: '新任务' })
      
      expect(taskApi.createTask).toHaveBeenCalled()
      expect(column.tasks).toHaveLength(0)
    })
  })

  describe('createColumn', () => {
    it('应该正确创建列', async () => {
      const store = useBoardStore()
      
      store.currentProject = createProject({ id: 1, columns: [] })
      
      const newColumn = createColumn({ id: 1, name: '新列', project_id: 1 })
      vi.mocked(columnApi.createColumn).mockResolvedValue(newColumn)
      
      await store.createColumn({ name: '新列' })
      
      expect(columnApi.createColumn).toHaveBeenCalledWith(1, { name: '新列' })
      expect(store.currentProject!.columns).toHaveLength(1)
      expect(store.currentProject!.columns[0].name).toBe('新列')
    })

    it('当 currentProject 为 null 时应该直接返回', async () => {
      const store = useBoardStore()
      store.currentProject = null
      
      await store.createColumn({ name: '新列' })
      
      expect(columnApi.createColumn).not.toHaveBeenCalled()
    })
  })

  describe('updateColumn', () => {
    it('应该正确更新列', async () => {
      const store = useBoardStore()
      const column = createColumn({ id: 1, name: '原名称', tasks: [createTask()] })
      
      store.currentProject = createProject({ columns: [column] })
      
      const updatedColumn = { ...column, name: '新名称' }
      delete (updatedColumn as any).tasks
      vi.mocked(columnApi.updateColumn).mockResolvedValue(updatedColumn)
      
      await store.updateColumn(1, { name: '新名称' })
      
      expect(columnApi.updateColumn).toHaveBeenCalledWith(1, { name: '新名称' })
      expect(store.currentProject!.columns[0].name).toBe('新名称')
      // 验证任务被保留
      expect(store.currentProject!.columns[0].tasks).toHaveLength(1)
    })

    it('当 currentProject 为 null 时应该直接返回', async () => {
      const store = useBoardStore()
      store.currentProject = null
      
      await store.updateColumn(1, { name: '新名称' })
      
      expect(columnApi.updateColumn).not.toHaveBeenCalled()
    })

    it('当列不存在时不应该更新', async () => {
      const store = useBoardStore()
      const column = createColumn({ id: 1, name: '原名称' })
      
      store.currentProject = createProject({ columns: [column] })
      
      const updatedColumn = createColumn({ id: 999, name: '新名称' })
      vi.mocked(columnApi.updateColumn).mockResolvedValue(updatedColumn)
      
      await store.updateColumn(999, { name: '新名称' })
      
      expect(columnApi.updateColumn).toHaveBeenCalled()
      expect(store.currentProject!.columns[0].name).toBe('原名称')
    })
  })

  describe('deleteColumn', () => {
    it('应该正确删除列', async () => {
      const store = useBoardStore()
      const column1 = createColumn({ id: 1 })
      const column2 = createColumn({ id: 2 })
      
      store.currentProject = createProject({ columns: [column1, column2] })
      
      vi.mocked(columnApi.deleteColumn).mockResolvedValue(undefined)
      
      await store.deleteColumn(1)
      
      expect(columnApi.deleteColumn).toHaveBeenCalledWith(1)
      expect(store.currentProject!.columns).toHaveLength(1)
      expect(store.currentProject!.columns[0].id).toBe(2)
    })

    it('当 currentProject 为 null 时应该直接返回', async () => {
      const store = useBoardStore()
      store.currentProject = null
      
      await store.deleteColumn(1)
      
      expect(columnApi.deleteColumn).not.toHaveBeenCalled()
    })
  })

  describe('loadProject', () => {
    it('应该正确加载项目', async () => {
      const store = useBoardStore()
      const project = createProject({ id: 1, name: '测试项目' })
      
      vi.mocked(projectApi.getProject).mockResolvedValue(project)
      
      await store.loadProject(1)
      
      expect(projectApi.getProject).toHaveBeenCalledWith(1)
      expect(store.currentProject).toEqual(project)
      expect(store.loading).toBe(false)
    })

    it('加载过程中 loading 应该为 true', async () => {
      const store = useBoardStore()
      const project = createProject({ id: 1 })
      
      let loadingDuringCall = false
      vi.mocked(projectApi.getProject).mockImplementation(async () => {
        loadingDuringCall = store.loading
        return project
      })
      
      await store.loadProject(1)
      
      expect(loadingDuringCall).toBe(true)
      expect(store.loading).toBe(false)
    })
  })

  describe('clearProject', () => {
    it('应该清除当前项目', () => {
      const store = useBoardStore()
      store.currentProject = createProject({ id: 1 })
      
      store.clearProject()
      
      expect(store.currentProject).toBeNull()
    })
  })

  describe('computed properties', () => {
    it('columns 应该返回当前项目的列', () => {
      const store = useBoardStore()
      const column = createColumn({ id: 1 })
      
      store.currentProject = createProject({ columns: [column] })
      
      expect(store.columns).toEqual([column])
    })

    it('当 currentProject 为 null 时 columns 应该返回空数组', () => {
      const store = useBoardStore()
      store.currentProject = null
      
      expect(store.columns).toEqual([])
    })

    it('projectName 应该返回当前项目名称', () => {
      const store = useBoardStore()
      
      store.currentProject = createProject({ name: '测试项目' })
      
      expect(store.projectName).toBe('测试项目')
    })

    it('当 currentProject 为 null 时 projectName 应该返回空字符串', () => {
      const store = useBoardStore()
      store.currentProject = null
      
      expect(store.projectName).toBe('')
    })
  })
})
