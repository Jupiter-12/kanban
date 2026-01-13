<script setup lang="ts">
/**
 * 任务卡片组件
 */
import { ref, computed } from 'vue'
import { Delete, Calendar } from '@element-plus/icons-vue'
import type { Task } from '@/types'

const props = defineProps<{
  task: Task
  readonly?: boolean
}>()

const emit = defineEmits<{
  update: [title: string]
  delete: []
  click: []
}>()

const editing = ref(false)
const editTitle = ref('')

// 优先级颜色映射
const priorityColors: Record<string, string> = {
  high: '#f56c6c',
  medium: '#e6a23c',
  low: '#909399'
}

// 获取优先级颜色
const priorityColor = computed(() => priorityColors[props.task.priority] || priorityColors.medium)

// 格式化截止日期
const formattedDueDate = computed(() => {
  if (!props.task.due_date) return null
  const date = new Date(props.task.due_date)
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}/${day}`
})

// 判断是否过期（只有当截止日期早于今天零点时才算过期）
const isOverdue = computed(() => {
  if (!props.task.due_date) return false
  const dueDate = new Date(props.task.due_date)
  const today = new Date()
  // 将今天的时间设置为零点，只比较日期部分
  today.setHours(0, 0, 0, 0)
  return dueDate < today
})

// 获取负责人显示名称（首字母或名称缩写）
const assigneeInitial = computed(() => {
  if (!props.task.assignee) return null
  // 使用用户名的首字母
  const name = props.task.assignee.username
  return name.charAt(0).toUpperCase()
})

const assigneeName = computed(() => {
  if (!props.task.assignee) return null
  // 用户名为主，显示名称为辅
  const { username, display_name } = props.task.assignee
  if (display_name) {
    return `${username} (${display_name})`
  }
  return username
})

function startEdit(title: string, event: Event) {
  event.stopPropagation()
  editTitle.value = title
  editing.value = true
}

function cancelEdit() {
  editing.value = false
  editTitle.value = ''
}

function confirmEdit() {
  if (editTitle.value.trim()) {
    emit('update', editTitle.value.trim())
  }
  cancelEdit()
}

function handleClick() {
  if (!editing.value) {
    emit('click')
  }
}

function handleDelete(event: Event) {
  event.stopPropagation()
  emit('delete')
}
</script>

<template>
  <div class="task-card" @click="handleClick">
    <!-- 优先级指示条 -->
    <div
      class="priority-indicator"
      :style="{ backgroundColor: priorityColor }"
    />
    <div class="task-main">
      <div v-if="editing" class="task-edit" @click.stop>
        <el-input
          v-model="editTitle"
          type="textarea"
          :rows="2"
          @keyup.enter.exact="confirmEdit"
          @keyup.escape="cancelEdit"
          @blur="confirmEdit"
        />
      </div>
      <template v-else>
        <div class="task-content" @dblclick="!readonly && startEdit(task.title, $event)">
          {{ task.title }}
        </div>
        <div class="task-meta">
          <!-- 截止日期 -->
          <span
            v-if="formattedDueDate"
            class="task-due-date"
            :class="{ overdue: isOverdue }"
          >
            <el-icon><Calendar /></el-icon>
            {{ formattedDueDate }}
          </span>
          <!-- 负责人 -->
          <span
            v-if="assigneeInitial"
            class="task-assignee"
            :title="assigneeName || ''"
          >
            {{ assigneeInitial }}
          </span>
        </div>
      </template>
    </div>
    <div class="task-actions" v-if="!readonly" @click.stop>
      <el-button
        :icon="Delete"
        size="small"
        text
        type="danger"
        @click="handleDelete"
      />
    </div>
  </div>
</template>

<style scoped>
.task-card {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: box-shadow 0.2s;
  display: flex;
  overflow: hidden;
}

.task-card:hover {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.priority-indicator {
  width: 4px;
  flex-shrink: 0;
}

.task-main {
  flex: 1;
  padding: 8px 12px;
  min-width: 0;
}

.task-content {
  font-size: 14px;
  color: #303133;
  word-break: break-word;
  margin-bottom: 4px;
}

.task-edit {
  width: 100%;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.task-due-date {
  display: flex;
  align-items: center;
  gap: 2px;
}

.task-due-date.overdue {
  color: #f56c6c;
}

.task-assignee {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 500;
  margin-left: auto;
}

.task-actions {
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
  padding: 8px 8px 8px 0;
  display: flex;
  align-items: flex-start;
}

.task-card:hover .task-actions {
  opacity: 1;
}
</style>
