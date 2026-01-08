/**
 * 看板状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  ProjectDetail,
  ColumnWithTasks,
  Task,
  ColumnCreateRequest,
  ColumnUpdateRequest,
  TaskCreateRequest,
  TaskUpdateRequest
} from '@/types'
import * as projectApi from '@/api/project'
import * as columnApi from '@/api/column'
import * as taskApi from '@/api/task'

export const useBoardStore = defineStore('board', () => {
  // 状态
  const currentProject = ref<ProjectDetail | null>(null)
  const loading = ref(false)

  // 计算属性
  const columns = computed(() => currentProject.value?.columns || [])
  const projectName = computed(() => currentProject.value?.name || '')

  /**
   * 加载项目详情
   */
  async function loadProject(projectId: number): Promise<void> {
    loading.value = true
    try {
      currentProject.value = await projectApi.getProject(projectId)
    } finally {
      loading.value = false
    }
  }

  /**
   * 清除当前项目
   */
  function clearProject(): void {
    currentProject.value = null
  }

  /**
   * 创建列
   */
  async function createColumn(data: ColumnCreateRequest): Promise<void> {
    if (!currentProject.value) return

    const column = await columnApi.createColumn(currentProject.value.id, data)
    const newColumn: ColumnWithTasks = { ...column, tasks: [] }
    currentProject.value.columns.push(newColumn)
  }

  /**
   * 更新列
   */
  async function updateColumn(
    columnId: number,
    data: ColumnUpdateRequest
  ): Promise<void> {
    if (!currentProject.value) return

    const updatedColumn = await columnApi.updateColumn(columnId, data)
    const index = currentProject.value.columns.findIndex(
      (c) => c.id === columnId
    )
    if (index !== -1) {
      const tasks = currentProject.value.columns[index].tasks
      currentProject.value.columns[index] = { ...updatedColumn, tasks }
    }
  }

  /**
   * 删除列
   */
  async function deleteColumn(columnId: number): Promise<void> {
    if (!currentProject.value) return

    await columnApi.deleteColumn(columnId)
    currentProject.value.columns = currentProject.value.columns.filter(
      (c) => c.id !== columnId
    )
  }

  /**
   * 创建任务
   */
  async function createTask(
    columnId: number,
    data: TaskCreateRequest
  ): Promise<void> {
    if (!currentProject.value) return

    const task = await taskApi.createTask(columnId, data)
    const column = currentProject.value.columns.find((c) => c.id === columnId)
    if (column) {
      column.tasks.push(task)
    }
  }

  /**
   * 更新任务
   */
  async function updateTask(
    taskId: number,
    data: TaskUpdateRequest
  ): Promise<void> {
    if (!currentProject.value) return

    const updatedTask = await taskApi.updateTask(taskId, data)
    for (const column of currentProject.value.columns) {
      const taskIndex = column.tasks.findIndex((t) => t.id === taskId)
      if (taskIndex !== -1) {
        column.tasks[taskIndex] = updatedTask
        break
      }
    }
  }

  /**
   * 删除任务
   */
  async function deleteTask(taskId: number): Promise<void> {
    if (!currentProject.value) return

    await taskApi.deleteTask(taskId)
    for (const column of currentProject.value.columns) {
      const taskIndex = column.tasks.findIndex((t) => t.id === taskId)
      if (taskIndex !== -1) {
        column.tasks.splice(taskIndex, 1)
        break
      }
    }
  }

  /**
   * 根据ID获取列
   */
  function getColumnById(columnId: number): ColumnWithTasks | undefined {
    return currentProject.value?.columns.find((c) => c.id === columnId)
  }

  /**
   * 根据ID获取任务
   */
  function getTaskById(taskId: number): Task | undefined {
    if (!currentProject.value) return undefined
    for (const column of currentProject.value.columns) {
      const task = column.tasks.find((t) => t.id === taskId)
      if (task) return task
    }
    return undefined
  }

  return {
    // 状态
    currentProject,
    loading,
    // 计算属性
    columns,
    projectName,
    // 方法
    loadProject,
    clearProject,
    createColumn,
    updateColumn,
    deleteColumn,
    createTask,
    updateTask,
    deleteTask,
    getColumnById,
    getTaskById
  }
})
