<script setup lang="ts">
/**
 * 用户管理页面（仅所有者可见）
 */
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Delete, Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores'
import { getAllUsers, updateUserRole, updateUserInfo, createUser, deleteUser } from '@/api/user'
import type { User, UserRole, UserInfoUpdateRequest, UserRegisterRequest } from '@/types'

const authStore = useAuthStore()
const loading = ref(false)
const users = ref<User[]>([])

// 编辑对话框
const editDialogVisible = ref(false)
const editingUser = ref<User | null>(null)
const editForm = ref<UserInfoUpdateRequest>({
  display_name: '',
  email: '',
  password: '',
  is_active: true
})

// 创建用户对话框
const createDialogVisible = ref(false)
const createForm = ref<UserRegisterRequest>({
  username: '',
  email: '',
  password: '',
  display_name: ''
})

const currentUser = computed(() => authStore.currentUser)
const isOwner = computed(() => currentUser.value?.role === 'owner')

const roleLabels: Record<UserRole, string> = {
  owner: '所有者',
  admin: '管理员',
  user: '普通用户'
}

const roleTagTypes: Record<UserRole, 'danger' | 'warning' | 'info'> = {
  owner: 'danger',
  admin: 'warning',
  user: 'info'
}

async function fetchUsers() {
  loading.value = true
  try {
    users.value = await getAllUsers()
  } catch (error) {
    console.error('获取用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

async function handleRoleChange(user: User, newRole: UserRole) {
  if (user.id === currentUser.value?.id) {
    ElMessage.warning('不能修改自己的角色')
    return
  }
  if (newRole === 'owner') {
    ElMessage.warning('不能将用户设置为所有者')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要将用户 "${user.display_name || user.username}" 的角色修改为 "${roleLabels[newRole]}" 吗？`,
      '确认修改',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await updateUserRole(user.id, newRole)
    ElMessage.success('角色修改成功')
    await fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('修改角色失败:', error)
    }
  }
}

function handleEditUser(user: User) {
  editingUser.value = user
  editForm.value = {
    display_name: user.display_name || '',
    email: user.email,
    password: '',
    is_active: user.is_active
  }
  editDialogVisible.value = true
}

async function handleEditConfirm() {
  if (!editingUser.value) return

  // 构建更新数据，只包含有变化的字段
  const updateData: UserInfoUpdateRequest = {}

  if (editForm.value.display_name !== (editingUser.value.display_name || '')) {
    updateData.display_name = editForm.value.display_name
  }
  if (editForm.value.email !== editingUser.value.email) {
    updateData.email = editForm.value.email
  }
  if (editForm.value.password) {
    updateData.password = editForm.value.password
  }
  if (editForm.value.is_active !== editingUser.value.is_active) {
    updateData.is_active = editForm.value.is_active
  }

  // 如果没有任何变化
  if (Object.keys(updateData).length === 0) {
    editDialogVisible.value = false
    return
  }

  try {
    await updateUserInfo(editingUser.value.id, updateData)
    ElMessage.success('用户信息更新成功')
    editDialogVisible.value = false
    await fetchUsers()
  } catch (error) {
    console.error('更新用户信息失败:', error)
    ElMessage.error('更新用户信息失败')
  }
}

function handleCreateUser() {
  createForm.value = {
    username: '',
    email: '',
    password: '',
    display_name: ''
  }
  createDialogVisible.value = true
}

async function handleCreateConfirm() {
  if (!createForm.value.username || !createForm.value.email || !createForm.value.password) {
    ElMessage.warning('请填写必填字段')
    return
  }

  if (createForm.value.password.length < 6) {
    ElMessage.warning('密码至少需要6位')
    return
  }

  try {
    await createUser(createForm.value)
    ElMessage.success('用户创建成功')
    createDialogVisible.value = false
    await fetchUsers()
  } catch (error) {
    console.error('创建用户失败:', error)
    ElMessage.error('创建用户失败')
  }
}

async function handleDeleteUser(user: User) {
  if (user.id === currentUser.value?.id) {
    ElMessage.warning('不能删除自己的账户')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.display_name || user.username}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteUser(user.id)
    ElMessage.success('用户已删除')
    await fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      ElMessage.error('删除用户失败')
    }
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div class="user-manage-container">
    <div class="page-header">
      <div class="header-left">
        <h1>用户管理</h1>
        <p class="page-description">管理系统用户及其角色权限</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="handleCreateUser">
        创建用户
      </el-button>
    </div>

    <el-card v-loading="loading">
      <el-table :data="users" style="width: 100%">
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="display_name" label="显示名称" width="120">
          <template #default="{ row }">
            {{ row.display_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="roleTagTypes[row.role as UserRole]">
              {{ roleLabels[row.role as UserRole] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" v-if="isOwner" min-width="240">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                :icon="Edit"
                size="small"
                text
                type="primary"
                @click="handleEditUser(row)"
              >
                编辑
              </el-button>
              <template v-if="row.role !== 'owner' && row.id !== currentUser?.id">
                <el-select
                  :model-value="row.role"
                  placeholder="修改角色"
                  size="small"
                  style="width: 100px"
                  @change="(val: UserRole) => handleRoleChange(row, val)"
                >
                  <el-option label="管理员" value="admin" />
                  <el-option label="普通用户" value="user" />
                </el-select>
                <el-button
                  :icon="Delete"
                  size="small"
                  text
                  type="danger"
                  @click="handleDeleteUser(row)"
                >
                  删除
                </el-button>
              </template>
              <template v-else-if="row.role === 'owner'">
                <span class="owner-hint">系统所有者</span>
              </template>
              <template v-else>
                <span class="self-hint">当前用户</span>
              </template>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <div class="role-description">
      <h3>角色说明</h3>
      <ul>
        <li><el-tag type="danger" size="small">所有者</el-tag> 拥有所有权限，可以编辑所有项目、管理用户角色</li>
        <li><el-tag type="warning" size="small">管理员</el-tag> 可以编辑所有项目，但不能管理用户角色</li>
        <li><el-tag type="info" size="small">普通用户</el-tag> 只能编辑自己创建的项目</li>
      </ul>
    </div>

    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="`编辑用户: ${editingUser?.username || ''}`"
      width="500px"
    >
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="显示名称">
          <el-input v-model="editForm.display_name" placeholder="请输入显示名称" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" placeholder="请输入邮箱" type="email" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input
            v-model="editForm.password"
            placeholder="留空则不修改密码"
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="账户状态" v-if="editingUser?.id !== currentUser?.id">
          <el-switch
            v-model="editForm.is_active"
            active-text="正常"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditConfirm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 创建用户对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建用户"
      width="500px"
    >
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="用户名" required>
          <el-input v-model="createForm.username" placeholder="请输入用户名（3-50字符）" />
        </el-form-item>
        <el-form-item label="邮箱" required>
          <el-input v-model="createForm.email" placeholder="请输入邮箱" type="email" />
        </el-form-item>
        <el-form-item label="密码" required>
          <el-input
            v-model="createForm.password"
            placeholder="请输入密码（至少6位）"
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="显示名称">
          <el-input v-model="createForm.display_name" placeholder="请输入显示名称（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateConfirm">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.user-manage-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-left h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.page-description {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.owner-hint,
.self-hint {
  color: #909399;
  font-size: 12px;
}

.role-description {
  margin-top: 24px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.role-description h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #606266;
}

.role-description ul {
  margin: 0;
  padding-left: 20px;
}

.role-description li {
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

.role-description li:last-child {
  margin-bottom: 0;
}
</style>
