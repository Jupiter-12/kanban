<script setup lang="ts">
/**
 * 个人设置页面
 */
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores'
import { updateMyProfile } from '@/api/user'
import type { UserSelfUpdateRequest } from '@/types'

const authStore = useAuthStore()
const loading = ref(false)

const currentUser = computed(() => authStore.currentUser)

// 基本信息表单
const profileForm = ref({
  display_name: '',
  email: ''
})

// 密码修改表单
const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const roleLabels: Record<string, string> = {
  owner: '所有者',
  admin: '管理员',
  user: '普通用户'
}

onMounted(() => {
  if (currentUser.value) {
    profileForm.value = {
      display_name: currentUser.value.display_name || '',
      email: currentUser.value.email
    }
  }
})

async function handleUpdateProfile() {
  if (!currentUser.value) return

  // 构建更新数据
  const updateData: UserSelfUpdateRequest = {}

  if (profileForm.value.display_name !== (currentUser.value.display_name || '')) {
    updateData.display_name = profileForm.value.display_name
  }
  if (profileForm.value.email !== currentUser.value.email) {
    updateData.email = profileForm.value.email
  }

  if (Object.keys(updateData).length === 0) {
    ElMessage.info('没有需要更新的内容')
    return
  }

  loading.value = true
  try {
    const updatedUser = await updateMyProfile(updateData)
    // 更新本地用户信息
    authStore.setUser(updatedUser)
    ElMessage.success('个人信息更新成功')
  } catch (error) {
    console.error('更新个人信息失败:', error)
    ElMessage.error('更新个人信息失败')
  } finally {
    loading.value = false
  }
}

async function handleChangePassword() {
  if (!passwordForm.value.current_password) {
    ElMessage.warning('请输入当前密码')
    return
  }
  if (!passwordForm.value.new_password) {
    ElMessage.warning('请输入新密码')
    return
  }
  if (passwordForm.value.new_password.length < 6) {
    ElMessage.warning('新密码至少需要6位')
    return
  }
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  loading.value = true
  try {
    await updateMyProfile({
      current_password: passwordForm.value.current_password,
      new_password: passwordForm.value.new_password
    })
    ElMessage.success('密码修改成功')
    // 清空密码表单
    passwordForm.value = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('修改密码失败，请检查当前密码是否正确')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="profile-container">
    <div class="page-header">
      <h1>个人设置</h1>
      <p class="page-description">查看和修改您的个人信息</p>
    </div>

    <div class="profile-content">
      <!-- 账户信息 -->
      <el-card class="profile-card">
        <template #header>
          <span class="card-title">账户信息</span>
        </template>
        <div class="info-item">
          <span class="info-label">用户名</span>
          <span class="info-value">{{ currentUser?.username }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">角色</span>
          <el-tag :type="currentUser?.role === 'owner' ? 'danger' : currentUser?.role === 'admin' ? 'warning' : 'info'">
            {{ roleLabels[currentUser?.role || 'user'] }}
          </el-tag>
        </div>
        <div class="info-item">
          <span class="info-label">注册时间</span>
          <span class="info-value">{{ currentUser?.created_at ? new Date(currentUser.created_at).toLocaleString() : '-' }}</span>
        </div>
      </el-card>

      <!-- 基本信息 -->
      <el-card class="profile-card">
        <template #header>
          <span class="card-title">基本信息</span>
        </template>
        <el-form :model="profileForm" label-width="100px" v-loading="loading">
          <el-form-item label="显示名称">
            <el-input v-model="profileForm.display_name" placeholder="请输入显示名称" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="profileForm.email" placeholder="请输入邮箱" type="email" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleUpdateProfile">保存修改</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 修改密码 -->
      <el-card class="profile-card">
        <template #header>
          <span class="card-title">修改密码</span>
        </template>
        <el-form :model="passwordForm" label-width="100px" v-loading="loading">
          <el-form-item label="当前密码">
            <el-input
              v-model="passwordForm.current_password"
              placeholder="请输入当前密码"
              type="password"
              show-password
            />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input
              v-model="passwordForm.new_password"
              placeholder="请输入新密码（至少6位）"
              type="password"
              show-password
            />
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input
              v-model="passwordForm.confirm_password"
              placeholder="请再次输入新密码"
              type="password"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleChangePassword">修改密码</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.profile-container {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.page-description {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.profile-card {
  width: 100%;
}

.card-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  width: 100px;
  color: #909399;
  font-size: 14px;
}

.info-value {
  color: #303133;
  font-size: 14px;
}
</style>
