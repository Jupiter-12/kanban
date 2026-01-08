<script setup lang="ts">
/**
 * 任务卡片组件
 */
import { ref } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import type { Task } from '@/types'

defineProps<{
  task: Task
}>()

const emit = defineEmits<{
  update: [title: string]
  delete: []
}>()

const editing = ref(false)
const editTitle = ref('')

function startEdit(title: string) {
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
</script>

<template>
  <div class="task-card">
    <div v-if="editing" class="task-edit">
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
      <div class="task-content" @dblclick="startEdit(task.title)">
        {{ task.title }}
      </div>
      <div class="task-actions">
        <el-button
          :icon="Delete"
          size="small"
          text
          type="danger"
          @click="emit('delete')"
        />
      </div>
    </template>
  </div>
</template>

<style scoped>
.task-card {
  background: #fff;
  border-radius: 4px;
  padding: 8px 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: box-shadow 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.task-card:hover {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.task-content {
  flex: 1;
  font-size: 14px;
  color: #303133;
  word-break: break-word;
}

.task-edit {
  width: 100%;
}

.task-actions {
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.task-card:hover .task-actions {
  opacity: 1;
}
</style>
