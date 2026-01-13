<script setup lang="ts">
/**
 * 看板视图页面
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import { useBoardStore, useAuthStore } from '@/stores'
import BoardColumn from '@/components/BoardColumn.vue'
import TaskDetailDialog from '@/components/TaskDetailDialog.vue'
import type { ColumnWithTasks, Task, TaskPriority } from '@/types'

/** 列拖拽变更事件类型 */
interface ColumnDragChangeEvent {
  moved?: { newIndex: number; oldIndex: number; element: ColumnWithTasks }
}

const route = useRoute()
const router = useRouter()
const boardStore = useBoardStore()
const authStore = useAuthStore()

const newColumnName = ref('')
const addingColumn = ref(false)

// 任务详情弹窗状态
const taskDialogVisible = ref(false)
const selectedTask = ref<Task | null>(null)

const projectId = computed(() => {
  const id = Number(route.params.id)
  return Number.isNaN(id) ? null : id
})

// 当前用户ID和角色
const currentUserId = computed(() => authStore.currentUser?.id)
const currentUserRole = computed(() => authStore.currentUser?.role)

// 判断当前用户是否有编辑权限
const canEdit = computed(() => {
  // 所有者和管理员可以编辑任意项目
  if (currentUserRole.value === 'owner' || currentUserRole.value === 'admin') {
    return true
  }
  // 普通用户只能编辑自己创建的项目
  return boardStore.currentProject?.owner_id === currentUserId.value
})

// 是否为只读模式
const isReadonly = computed(() => !canEdit.value)

onMounted(async () => {
  if (projectId.value === null) {
    ElMessage.error('无效的项目ID')
    router.push('/projects')
    return
  }
  await boardStore.loadProject(projectId.value)
})

onUnmounted(() => {
  boardStore.clearProject()
})

function goBack() {
  // 使用浏览器历史返回，保持用户的导航上下文
  router.back()
}

function startAddColumn() {
  addingColumn.value = true
  newColumnName.value = ''
}

function cancelAddColumn() {
  addingColumn.value = false
  newColumnName.value = ''
}

async function confirmAddColumn() {
  if (!newColumnName.value.trim()) {
    ElMessage.warning('列名称不能为空')
    return
  }
  try {
    await boardStore.createColumn({ name: newColumnName.value.trim() })
    ElMessage.success('列已创建')
    cancelAddColumn()
  } catch {
    ElMessage.error('创建列失败')
  }
}

async function handleUpdateColumn(columnId: number, name: string) {
  try {
    await boardStore.updateColumn(columnId, { name })
    ElMessage.success('列已更新')
  } catch {
    ElMessage.error('更新列失败')
  }
}

async function handleDeleteColumn(columnId: number) {
  try {
    await ElMessageBox.confirm(
      '删除列将同时删除该列中的所有任务，此操作不可恢复。确定要删除吗？',
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await boardStore.deleteColumn(columnId)
    ElMessage.success('列已删除')
  } catch (error) {
    // 用户取消确认框时 error 为 'cancel'
    if (error !== 'cancel') {
      ElMessage.error('删除列失败')
    }
  }
}

async function handleCreateTask(columnId: number, title: string) {
  try {
    await boardStore.createTask(columnId, { title })
    ElMessage.success('任务已创建')
  } catch {
    ElMessage.error('创建任务失败')
  }
}

async function handleUpdateTask(taskId: number, title: string) {
  try {
    await boardStore.updateTask(taskId, { title })
    ElMessage.success('任务已更新')
  } catch {
    ElMessage.error('更新任务失败')
  }
}

async function handleDeleteTask(taskId: number) {
  try {
    await boardStore.deleteTask(taskId)
    ElMessage.success('任务已删除')
  } catch {
    ElMessage.error('删除任务失败')
  }
}

/**
 * 处理任务移动
 */
async function handleMoveTask(
  taskId: number,
  sourceColumnId: number,
  targetColumnId: number,
  newPosition: number
) {
  try {
    await boardStore.moveTask(taskId, sourceColumnId, targetColumnId, newPosition)
  } catch {
    ElMessage.error('移动任务失败')
  }
}

/**
 * 处理列拖拽排序
 */
async function onColumnChange(event: ColumnDragChangeEvent) {
  if (event.moved) {
    const columnIds = boardStore.columns.map((c) => c.id)
    try {
      await boardStore.reorderColumns(columnIds)
    } catch {
      ElMessage.error('列排序失败')
    }
  }
}

/**
 * 处理任务卡片点击，打开详情弹窗
 */
function handleClickTask(task: Task) {
  // 从 store 获取最新的任务数据
  const latestTask = boardStore.getTaskById(task.id)
  selectedTask.value = latestTask || task
  taskDialogVisible.value = true
}

/**
 * 处理任务详情弹窗关闭
 */
function handleTaskDialogClose() {
  // 关闭弹窗时，更新 selectedTask 为 store 中的最新数据
  if (selectedTask.value) {
    const latestTask = boardStore.getTaskById(selectedTask.value.id)
    if (latestTask) {
      selectedTask.value = latestTask
    }
  }
}

/**
 * 处理任务详情更新
 */
async function handleTaskDetailConfirm(data: {
  title: string
  description: string | null
  due_date: string | null
  priority: TaskPriority
  assignee_id: number | null
}) {
  if (!selectedTask.value) return
  try {
    await boardStore.updateTask(selectedTask.value.id, data)
    // 更新成功后，同步更新 selectedTask 为最新数据
    const updatedTask = boardStore.getTaskById(selectedTask.value.id)
    if (updatedTask) {
      selectedTask.value = updatedTask
    }
    ElMessage.success('任务已更新')
  } catch {
    ElMessage.error('更新任务失败')
  }
}
</script>

<template>
  <div class="board-view">
    <div class="board-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h1>{{ boardStore.projectName }}</h1>
        <el-tag v-if="isReadonly" type="info" size="small">只读</el-tag>
      </div>
    </div>

    <div v-if="boardStore.loading" class="loading">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else class="board-content">
      <div class="columns-container">
        <draggable
          :list="boardStore.columns"
          item-key="id"
          class="columns-draggable"
          handle=".column-header"
          :animation="150"
          :disabled="isReadonly"
          @change="onColumnChange"
        >
          <template #item="{ element: column }">
            <BoardColumn
              :column="column"
              :readonly="isReadonly"
              @update-column="handleUpdateColumn"
              @delete-column="handleDeleteColumn"
              @create-task="handleCreateTask"
              @update-task="handleUpdateTask"
              @delete-task="handleDeleteTask"
              @move-task="handleMoveTask"
              @click-task="handleClickTask"
            />
          </template>
        </draggable>

        <div class="add-column" v-if="!isReadonly">
          <div v-if="addingColumn" class="add-column-form">
            <el-input
              v-model="newColumnName"
              placeholder="输入列名称"
              @keyup.enter="confirmAddColumn"
              @keyup.escape="cancelAddColumn"
            />
            <div class="add-column-actions">
              <el-button type="primary" size="small" @click="confirmAddColumn">
                添加
              </el-button>
              <el-button size="small" @click="cancelAddColumn">取消</el-button>
            </div>
          </div>
          <el-button
            v-else
            class="add-column-btn"
            :icon="Plus"
            @click="startAddColumn"
          >
            添加列
          </el-button>
        </div>
      </div>
    </div>

    <!-- 任务详情弹窗 -->
    <TaskDetailDialog
      v-model:visible="taskDialogVisible"
      :task="selectedTask"
      :readonly="isReadonly"
      @confirm="handleTaskDetailConfirm"
      @close="handleTaskDialogClose"
    />
  </div>
</template>

<style scoped>
.board-view {
  height: calc(100vh - 60px - 48px);
  display: flex;
  flex-direction: column;
}

.board-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h1 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.loading {
  padding: 24px;
}

.board-content {
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
}

.columns-container {
  display: flex;
  gap: 16px;
  height: 100%;
  padding-bottom: 16px;
}

.columns-draggable {
  display: flex;
  gap: 16px;
}

.add-column {
  flex-shrink: 0;
  width: 280px;
}

.add-column-form {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.add-column-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.add-column-btn {
  width: 100%;
  height: 40px;
  background: rgba(255, 255, 255, 0.8);
  border: 2px dashed #dcdfe6;
}

.add-column-btn:hover {
  border-color: #409eff;
  color: #409eff;
}
</style>
