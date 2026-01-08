<script setup lang="ts">
/**
 * 项目卡片组件
 */
import { Edit, Delete } from '@element-plus/icons-vue'
import type { Project } from '@/types'

defineProps<{
  project: Project
}>()

const emit = defineEmits<{
  click: []
  edit: []
  delete: []
}>()

function handleEdit(event: Event) {
  event.stopPropagation()
  emit('edit')
}

function handleDelete(event: Event) {
  event.stopPropagation()
  emit('delete')
}
</script>

<template>
  <el-card class="project-card" shadow="hover" @click="emit('click')">
    <div class="card-header">
      <h3 class="project-name">{{ project.name }}</h3>
      <div class="card-actions">
        <el-button
          :icon="Edit"
          size="small"
          text
          @click="handleEdit"
        />
        <el-button
          :icon="Delete"
          size="small"
          text
          type="danger"
          @click="handleDelete"
        />
      </div>
    </div>
    <p class="project-description">
      {{ project.description || '暂无描述' }}
    </p>
    <div class="project-meta">
      <span>创建于 {{ new Date(project.created_at).toLocaleDateString() }}</span>
    </div>
  </el-card>
</template>

<style scoped>
.project-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.project-card:hover {
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.project-name {
  margin: 0;
  font-size: 16px;
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.project-card:hover .card-actions {
  opacity: 1;
}

.project-description {
  margin: 0 0 12px;
  font-size: 14px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.project-meta {
  font-size: 12px;
  color: #c0c4cc;
}
</style>
