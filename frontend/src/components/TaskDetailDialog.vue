<script setup lang="ts">
/**
 * 任务详情对话框组件
 */
import { ref, watch, computed, onMounted } from 'vue'
import { getUsers } from '@/api'
import CommentSection from './CommentSection.vue'
import type { Task, TaskPriority, UserListItem } from '@/types'

const props = defineProps<{
  visible: boolean
  task: Task | null
  readonly?: boolean
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  confirm: [data: {
    title: string
    description: string | null
    due_date: string | null
    priority: TaskPriority
    assignee_id: number | null
  }]
  close: []
}>()

const form = ref({
  title: '',
  description: '',
  due_date: null as Date | null,
  priority: 'medium' as TaskPriority,
  assignee_id: null as number | null
})

const formRef = ref()
const users = ref<UserListItem[]>([])
const loadingUsers = ref(false)

const rules = {
  title: [
    { required: true, message: '请输入任务标题', trigger: 'blur' },
    { min: 1, max: 200, message: '任务标题长度为1-200个字符', trigger: 'blur' }
  ]
}

const priorityOptions = [
  { value: 'high', label: '高', color: '#f56c6c' },
  { value: 'medium', label: '中', color: '#e6a23c' },
  { value: 'low', label: '低', color: '#909399' }
]

const dialogTitle = computed(() => {
  if (props.readonly) return '查看任务'
  return props.task ? '编辑任务' : '创建任务'
})

watch(
  () => props.visible,
  (val) => {
    if (val) {
      if (props.task) {
        form.value = {
          title: props.task.title,
          description: props.task.description || '',
          due_date: props.task.due_date ? new Date(props.task.due_date) : null,
          priority: props.task.priority,
          assignee_id: props.task.assignee_id
        }
      } else {
        form.value = {
          title: '',
          description: '',
          due_date: null,
          priority: 'medium',
          assignee_id: null
        }
      }
    }
  }
)

async function loadUsers() {
  if (users.value.length > 0) return
  loadingUsers.value = true
  try {
    users.value = await getUsers()
  } catch (error) {
    console.error('加载用户列表失败:', error)
  } finally {
    loadingUsers.value = false
  }
}

onMounted(() => {
  loadUsers()
})

function handleClose() {
  emit('update:visible', false)
  emit('close')
  formRef.value?.resetFields()
}

async function handleConfirm() {
  try {
    await formRef.value?.validate()
    emit('confirm', {
      title: form.value.title,
      description: form.value.description || null,
      due_date: form.value.due_date ? form.value.due_date.toISOString() : null,
      priority: form.value.priority,
      // Element Plus select 清除时可能设置为 undefined，需要转换为 null
      assignee_id: form.value.assignee_id ?? null
    })
    handleClose()
  } catch {
    // 验证失败
  }
}

function getUserDisplayName(user: UserListItem): string {
  // 用户名为主，显示名称为辅
  if (user.display_name) {
    return `${user.username} (${user.display_name})`
  }
  return user.username
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    :title="dialogTitle"
    width="600px"
    :close-on-press-escape="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="80px"
    >
      <el-form-item label="标题" prop="title">
        <el-input
          v-model="form.title"
          placeholder="请输入任务标题"
          maxlength="200"
          show-word-limit
          :disabled="readonly"
        />
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          placeholder="请输入任务描述（可选）"
          :rows="4"
          :disabled="readonly"
        />
      </el-form-item>
      <el-form-item label="截止日期" prop="due_date">
        <el-date-picker
          v-model="form.due_date"
          type="datetime"
          placeholder="选择截止日期"
          format="YYYY-MM-DD HH:mm"
          style="width: 100%"
          :disabled="readonly"
        />
      </el-form-item>
      <el-form-item label="优先级" prop="priority">
        <el-select v-model="form.priority" style="width: 100%" :disabled="readonly">
          <el-option
            v-for="option in priorityOptions"
            :key="option.value"
            :value="option.value"
            :label="option.label"
          >
            <span class="priority-option">
              <span
                class="priority-dot"
                :style="{ backgroundColor: option.color }"
              />
              {{ option.label }}
            </span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="负责人" prop="assignee_id">
        <el-select
          v-model="form.assignee_id"
          placeholder="选择负责人（可选）"
          clearable
          :loading="loadingUsers"
          style="width: 100%"
          :disabled="readonly"
        >
          <el-option
            v-for="user in users"
            :key="user.id"
            :value="user.id"
            :label="getUserDisplayName(user)"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <!-- 评论区 -->
    <CommentSection
      v-if="task"
      :task-id="task.id"
      :readonly="readonly"
    />

    <template #footer>
      <el-button @click="handleClose">{{ readonly ? '关闭' : '取消' }}</el-button>
      <el-button v-if="!readonly" type="primary" @click="handleConfirm">
        {{ task ? '保存' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.priority-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.priority-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
</style>
