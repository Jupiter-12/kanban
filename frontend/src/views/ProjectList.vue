<script setup lang="ts">
/**
 * 项目列表页面
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useProjectStore } from '@/stores'
import ProjectCard from '@/components/ProjectCard.vue'
import ProjectDialog from '@/components/ProjectDialog.vue'

const router = useRouter()
const projectStore = useProjectStore()

const dialogVisible = ref(false)
const editingProject = ref<{ id: number; name: string; description: string } | null>(null)

onMounted(async () => {
  await projectStore.fetchProjects()
})

function handleCreate() {
  editingProject.value = null
  dialogVisible.value = true
}

function handleEdit(project: { id: number; name: string; description: string | null }) {
  editingProject.value = {
    id: project.id,
    name: project.name,
    description: project.description || ''
  }
  dialogVisible.value = true
}

async function handleDelete(projectId: number) {
  try {
    await ElMessageBox.confirm(
      '删除项目将同时删除所有列和任务，此操作不可恢复。确定要删除吗？',
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await projectStore.deleteProject(projectId)
    ElMessage.success('项目已删除')
  } catch {
    // 用户取消
  }
}

function handleClick(projectId: number) {
  router.push(`/projects/${projectId}`)
}

async function handleDialogConfirm(data: { name: string; description: string }) {
  try {
    if (editingProject.value) {
      await projectStore.updateProject(editingProject.value.id, data)
      ElMessage.success('项目已更新')
    } else {
      await projectStore.createProject(data)
      ElMessage.success('项目已创建')
    }
    dialogVisible.value = false
  } catch {
    ElMessage.error(editingProject.value ? '更新项目失败' : '创建项目失败')
  }
}
</script>

<template>
  <div class="project-list">
    <div class="page-header">
      <h1>我的项目</h1>
      <el-button type="primary" :icon="Plus" @click="handleCreate">
        创建项目
      </el-button>
    </div>

    <div v-if="projectStore.loading" class="loading">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="projectStore.projects.length === 0" class="empty">
      <el-empty description="暂无项目">
        <el-button type="primary" @click="handleCreate">创建第一个项目</el-button>
      </el-empty>
    </div>

    <div v-else class="project-grid">
      <ProjectCard
        v-for="project in projectStore.projects"
        :key="project.id"
        :project="project"
        @click="handleClick(project.id)"
        @edit="handleEdit(project)"
        @delete="handleDelete(project.id)"
      />
    </div>

    <ProjectDialog
      v-model:visible="dialogVisible"
      :project="editingProject"
      @confirm="handleDialogConfirm"
    />
  </div>
</template>

<style scoped>
.project-list {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.loading {
  padding: 24px;
}

.empty {
  padding: 48px;
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}
</style>
