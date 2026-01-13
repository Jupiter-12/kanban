<script setup lang="ts">
/**
 * 项目列表页面
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useProjectStore, useAuthStore } from '@/stores'
import ProjectCard from '@/components/ProjectCard.vue'
import ProjectDialog from '@/components/ProjectDialog.vue'

const router = useRouter()
const route = useRoute()
const projectStore = useProjectStore()
const authStore = useAuthStore()

const dialogVisible = ref(false)
const editingProject = ref<{ id: number; name: string; description: string } | null>(null)

const currentUserId = computed(() => authStore.currentUser?.id)
const currentUserRole = computed(() => authStore.currentUser?.role)

// 是否可以编辑所有项目（所有者或管理员）
const canEditAllProjects = computed(() =>
  currentUserRole.value === 'owner' || currentUserRole.value === 'admin'
)

// 当前过滤模式
const filterMode = computed(() => route.meta.filter as string || 'my')

// 页面标题
const pageTitle = computed(() => filterMode.value === 'my' ? '我的项目' : '所有项目')

// 过滤后的项目列表
const filteredProjects = computed(() => {
  if (filterMode.value === 'my') {
    return projectStore.projects.filter(p => p.owner_id === currentUserId.value)
  }
  return projectStore.projects
})

// 判断项目是否可编辑
function canEditProject(projectOwnerId: number): boolean {
  if (canEditAllProjects.value) return true
  return projectOwnerId === currentUserId.value
}

onMounted(async () => {
  await projectStore.fetchProjects()
})

// 监听路由变化，重新获取项目
watch(() => route.path, async () => {
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
      <h1>{{ pageTitle }}</h1>
      <el-button type="primary" :icon="Plus" @click="handleCreate">
        创建项目
      </el-button>
    </div>

    <div v-if="projectStore.loading" class="loading">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="filteredProjects.length === 0" class="empty">
      <el-empty :description="filterMode === 'my' ? '暂无我的项目' : '暂无项目'">
        <el-button type="primary" @click="handleCreate">创建第一个项目</el-button>
      </el-empty>
    </div>

    <div v-else class="project-grid">
      <ProjectCard
        v-for="project in filteredProjects"
        :key="project.id"
        :project="project"
        :readonly="!canEditProject(project.owner_id)"
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
