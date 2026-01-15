<script setup lang="ts">
/**
 * 任务筛选栏组件
 */
import { ref, onMounted, computed } from 'vue'
import { Search, RefreshRight } from '@element-plus/icons-vue'
import { getUsers } from '@/api'
import type { TaskFilterParams, TaskPriority, UserListItem } from '@/types'

const props = defineProps<{
  modelValue: TaskFilterParams
}>()

const emit = defineEmits<{
  'update:modelValue': [value: TaskFilterParams]
  search: [filter: TaskFilterParams]
  clear: []
}>()

const users = ref<UserListItem[]>([])
const loadingUsers = ref(false)

const filter = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const priorityOptions = [
  { value: 'high', label: '高', color: '#f56c6c' },
  { value: 'medium', label: '中', color: '#e6a23c' },
  { value: 'low', label: '低', color: '#909399' }
]

const hasFilter = computed(() => {
  const f = filter.value
  return !!(
    f.keyword ||
    (f.assignee_id !== undefined && f.assignee_id !== null) ||
    f.priority ||
    f.due_date_start ||
    f.due_date_end
  )
})

async function loadUsers() {
  loadingUsers.value = true
  try {
    users.value = await getUsers()
  } catch (error) {
    console.error('加载用户列表失败:', error)
  } finally {
    loadingUsers.value = false
  }
}

function handleSearch() {
  emit('search', filter.value)
}

function handleClear() {
  filter.value = {}
  emit('clear')
}

function getUserDisplayName(user: UserListItem): string {
  if (user.display_name) {
    return `${user.username} (${user.display_name})`
  }
  return user.username
}

onMounted(() => {
  loadUsers()
})
</script>

<template>
  <div class="task-filter">
    <el-input
      v-model="filter.keyword"
      placeholder="搜索任务标题..."
      clearable
      :prefix-icon="Search"
      class="filter-input"
      @keyup.enter="handleSearch"
      @clear="handleSearch"
    />

    <el-select
      v-model="filter.assignee_id"
      placeholder="负责人"
      clearable
      :loading="loadingUsers"
      class="filter-select"
      @change="handleSearch"
    >
      <el-option
        v-for="user in users"
        :key="user.id"
        :value="user.id"
        :label="getUserDisplayName(user)"
      />
    </el-select>

    <el-select
      v-model="filter.priority"
      placeholder="优先级"
      clearable
      class="filter-select"
      @change="handleSearch"
    >
      <el-option
        v-for="option in priorityOptions"
        :key="option.value"
        :value="option.value"
        :label="option.label"
      >
        <span class="priority-option">
          <span class="priority-dot" :style="{ backgroundColor: option.color }" />
          {{ option.label }}
        </span>
      </el-option>
    </el-select>

    <el-date-picker
      v-model="filter.due_date_start"
      type="date"
      placeholder="截止日期起始"
      format="YYYY-MM-DD"
      value-format="YYYY-MM-DD"
      class="filter-date"
      @change="handleSearch"
    />

    <el-date-picker
      v-model="filter.due_date_end"
      type="date"
      placeholder="截止日期结束"
      format="YYYY-MM-DD"
      value-format="YYYY-MM-DD"
      class="filter-date"
      @change="handleSearch"
    />

    <el-button
      v-if="hasFilter"
      :icon="RefreshRight"
      @click="handleClear"
    >
      清除筛选
    </el-button>
  </div>
</template>

<style scoped>
.task-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  padding: 12px 0;
}

.filter-input {
  width: 200px;
}

.filter-select {
  width: 140px;
}

.filter-date {
  width: 150px;
}

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
