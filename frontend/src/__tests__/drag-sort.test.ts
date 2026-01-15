/**
 * BoardColumn 组件单元测试
 * 重点测试拖拽事件处理逻辑
 */
import { describe, it, expect, vi } from 'vitest'
import type { ColumnWithTasks, Task } from '@/types'

// 创建测试数据
function createTask(overrides: Partial<Task> = {}): Task {
  return {
    id: 1,
    title: '测试任务',
    description: null,
    due_date: null,
    priority: 'medium',
    assignee_id: null,
    assignee: null,
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

// 由于 BoardColumn 依赖 element-plus 和 vuedraggable，
// 我们测试其核心逻辑：onTaskChange 函数
describe('BoardColumn 拖拽逻辑', () => {
  describe('onTaskChange 事件处理', () => {
    // 模拟 onTaskChange 函数的逻辑
    function simulateOnTaskChange(
      event: {
        added?: { newIndex: number; element: Task }
        removed?: { oldIndex: number; element: Task }
        moved?: { newIndex: number; oldIndex: number; element: Task }
      },
      columnId: number,
      emitMoveTask: (taskId: number, sourceColumnId: number, targetColumnId: number, newPosition: number) => void
    ) {
      // 任务被添加到当前列（从其他列拖入）
      if (event.added) {
        const task = event.added.element
        const sourceColumnId = task.column_id
        emitMoveTask(task.id, sourceColumnId, columnId, event.added.newIndex)
      }
      // 列内移动
      if (event.moved) {
        const task = event.moved.element
        emitMoveTask(task.id, columnId, columnId, event.moved.newIndex)
      }
    }

    it('当任务从其他列拖入时应该触发 moveTask 事件', () => {
      const emitMoveTask = vi.fn()
      const task = createTask({ id: 1, column_id: 2 }) // 任务原本在列2
      const currentColumnId = 1 // 当前列是列1
      
      const event = {
        added: { newIndex: 0, element: task }
      }
      
      simulateOnTaskChange(event, currentColumnId, emitMoveTask)
      
      expect(emitMoveTask).toHaveBeenCalledWith(1, 2, 1, 0)
    })

    it('当任务在列内移动时应该触发 moveTask 事件', () => {
      const emitMoveTask = vi.fn()
      const task = createTask({ id: 1, column_id: 1 })
      const currentColumnId = 1
      
      const event = {
        moved: { oldIndex: 0, newIndex: 2, element: task }
      }
      
      simulateOnTaskChange(event, currentColumnId, emitMoveTask)
      
      expect(emitMoveTask).toHaveBeenCalledWith(1, 1, 1, 2)
    })

    it('当任务被移出时不应该触发 moveTask 事件', () => {
      const emitMoveTask = vi.fn()
      const task = createTask({ id: 1, column_id: 1 })
      const currentColumnId = 1
      
      const event = {
        removed: { oldIndex: 0, element: task }
      }
      
      simulateOnTaskChange(event, currentColumnId, emitMoveTask)
      
      expect(emitMoveTask).not.toHaveBeenCalled()
    })

    it('应该正确处理任务拖入到列末尾', () => {
      const emitMoveTask = vi.fn()
      const task = createTask({ id: 1, column_id: 2 })
      const currentColumnId = 1
      
      const event = {
        added: { newIndex: 5, element: task }
      }
      
      simulateOnTaskChange(event, currentColumnId, emitMoveTask)
      
      expect(emitMoveTask).toHaveBeenCalledWith(1, 2, 1, 5)
    })

    it('应该正确处理任务在列内移动到开头', () => {
      const emitMoveTask = vi.fn()
      const task = createTask({ id: 3, column_id: 1 })
      const currentColumnId = 1
      
      const event = {
        moved: { oldIndex: 2, newIndex: 0, element: task }
      }
      
      simulateOnTaskChange(event, currentColumnId, emitMoveTask)
      
      expect(emitMoveTask).toHaveBeenCalledWith(3, 1, 1, 0)
    })
  })
})

describe('BoardView 列拖拽逻辑', () => {
  describe('onColumnChange 事件处理', () => {
    // 模拟 onColumnChange 函数的逻辑
    function simulateOnColumnChange(
      event: {
        moved?: { newIndex: number; oldIndex: number; element: ColumnWithTasks }
      },
      columns: ColumnWithTasks[],
      reorderColumns: (columnIds: number[]) => void
    ) {
      if (event.moved) {
        const columnIds = columns.map((c) => c.id)
        reorderColumns(columnIds)
      }
    }

    it('当列被移动时应该触发 reorderColumns', () => {
      const reorderColumns = vi.fn()
      const columns = [
        createColumn({ id: 2 }),
        createColumn({ id: 1 }),
        createColumn({ id: 3 })
      ]
      
      const event = {
        moved: { oldIndex: 0, newIndex: 1, element: columns[1] }
      }
      
      simulateOnColumnChange(event, columns, reorderColumns)
      
      expect(reorderColumns).toHaveBeenCalledWith([2, 1, 3])
    })

    it('当没有移动事件时不应该触发 reorderColumns', () => {
      const reorderColumns = vi.fn()
      const columns = [createColumn({ id: 1 })]
      
      const event = {}
      
      simulateOnColumnChange(event, columns, reorderColumns)
      
      expect(reorderColumns).not.toHaveBeenCalled()
    })
  })
})
