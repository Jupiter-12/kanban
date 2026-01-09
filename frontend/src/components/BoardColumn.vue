<script setup lang="ts">
/**
 * 看板列组件
 */
import { ref } from 'vue'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import type { ColumnWithTasks, Task } from '@/types'
import TaskCard from './TaskCard.vue'

/** 拖拽变更事件类型 */
interface DragChangeEvent {
  added?: { newIndex: number; element: Task }
  removed?: { oldIndex: number; element: Task }
  moved?: { newIndex: number; oldIndex: number; element: Task }
}

const props = defineProps<{
  column: ColumnWithTasks
}>()

const emit = defineEmits<{
  updateColumn: [columnId: number, name: string]
  deleteColumn: [columnId: number]
  createTask: [columnId: number, title: string]
  updateTask: [taskId: number, title: string]
  deleteTask: [taskId: number]
  moveTask: [taskId: number, sourceColumnId: number, targetColumnId: number, newPosition: number]
}>()

const editing = ref(false)
const editName = ref('')
const addingTask = ref(false)
const newTaskTitle = ref('')

function startEdit(name: string) {
  editName.value = name
  editing.value = true
}

function cancelEdit() {
  editing.value = false
  editName.value = ''
}

function confirmEdit(columnId: number) {
  if (editName.value.trim()) {
    emit('updateColumn', columnId, editName.value.trim())
  }
  cancelEdit()
}

function startAddTask() {
  addingTask.value = true
  newTaskTitle.value = ''
}

function cancelAddTask() {
  addingTask.value = false
  newTaskTitle.value = ''
}

function confirmAddTask(columnId: number) {
  if (newTaskTitle.value.trim()) {
    emit('createTask', columnId, newTaskTitle.value.trim())
  }
  cancelAddTask()
}

/**
 * 处理任务拖拽变更
 * 注意：vuedraggable 在触发 change 事件前已经更新了数组
 * 但 task.column_id 属性还未更新，仍然是源列 ID
 */
function onTaskChange(event: DragChangeEvent) {
  // 任务被添加到当前列（从其他列拖入）
  if (event.added) {
    const task = event.added.element
    // 此时 task.column_id 仍然是源列 ID（vuedraggable 只移动了数组元素，未修改属性）
    const sourceColumnId = task.column_id
    emit('moveTask', task.id, sourceColumnId, props.column.id, event.added.newIndex)
  }
  // 列内移动
  if (event.moved) {
    const task = event.moved.element
    emit('moveTask', task.id, props.column.id, props.column.id, event.moved.newIndex)
  }
}
</script>

<template>
  <div class="board-column">
    <div class="column-header">
      <div v-if="editing" class="column-edit">
        <el-input
          v-model="editName"
          size="small"
          @keyup.enter="confirmEdit(column.id)"
          @keyup.escape="cancelEdit"
          @blur="confirmEdit(column.id)"
        />
      </div>
      <h3 v-else class="column-title" @dblclick="startEdit(column.name)">
        {{ column.name }}
        <span class="task-count">({{ column.tasks.length }})</span>
      </h3>
      <div class="column-actions">
        <el-button
          :icon="Edit"
          size="small"
          text
          @click="startEdit(column.name)"
        />
        <el-button
          :icon="Delete"
          size="small"
          text
          type="danger"
          @click="emit('deleteColumn', column.id)"
        />
      </div>
    </div>

    <div class="column-content">
      <draggable
        :list="column.tasks"
        group="tasks"
        item-key="id"
        class="task-list"
        :animation="150"
        @change="onTaskChange"
      >
        <template #item="{ element: task }">
          <TaskCard
            :task="task"
            @update="(title) => emit('updateTask', task.id, title)"
            @delete="emit('deleteTask', task.id)"
          />
        </template>
      </draggable>

      <div v-if="addingTask" class="add-task-form">
        <el-input
          v-model="newTaskTitle"
          type="textarea"
          :rows="2"
          placeholder="输入任务标题"
          @keyup.enter.exact="confirmAddTask(column.id)"
          @keyup.escape="cancelAddTask"
        />
        <div class="add-task-actions">
          <el-button
            type="primary"
            size="small"
            @click="confirmAddTask(column.id)"
          >
            添加
          </el-button>
          <el-button size="small" @click="cancelAddTask">取消</el-button>
        </div>
      </div>
    </div>

    <div class="column-footer">
      <el-button
        v-if="!addingTask"
        class="add-task-btn"
        :icon="Plus"
        text
        @click="startAddTask"
      >
        添加任务
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.board-column {
  flex-shrink: 0;
  width: 280px;
  background: #f4f5f7;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  max-height: 100%;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.column-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  cursor: pointer;
}

.column-title:hover {
  color: #409eff;
}

.task-count {
  font-weight: normal;
  color: #909399;
  margin-left: 4px;
}

.column-edit {
  flex: 1;
  margin-right: 8px;
}

.column-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.board-column:hover .column-actions {
  opacity: 1;
}

.column-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 20px;
}

.task-list:empty {
  min-height: 60px;
}

.add-task-form {
  background: #fff;
  border-radius: 4px;
  padding: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.add-task-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.column-footer {
  padding: 8px 12px;
}

.add-task-btn {
  width: 100%;
  justify-content: flex-start;
  color: #909399;
}

.add-task-btn:hover {
  color: #409eff;
  background: rgba(64, 158, 255, 0.1);
}
</style>
