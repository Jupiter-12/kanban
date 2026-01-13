<script setup lang="ts">
/**
 * 应用头部导航栏
 */
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const user = computed(() => authStore.currentUser)
const displayName = computed(() => user.value?.display_name || user.value?.username || '')
const isOwner = computed(() => user.value?.role === 'owner')
const roleLabel = computed(() => {
  const labels: Record<string, string> = {
    owner: '所有者',
    admin: '管理员',
    user: '普通用户'
  }
  return labels[user.value?.role || 'user'] || '普通用户'
})

function goToProjects() {
  router.push('/projects')
}

function goToUserManage() {
  router.push('/users')
}

function goToProfile() {
  router.push('/profile')
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch {
    // 用户取消
  }
}
</script>

<template>
  <el-header class="app-header">
    <div class="header-left">
      <h1 class="app-title" @click="goToProjects">看板系统</h1>
      <el-menu
        mode="horizontal"
        :default-active="route.path"
        :ellipsis="false"
        class="header-menu"
        router
      >
        <el-menu-item index="/projects/my">我的项目</el-menu-item>
        <el-menu-item index="/projects/all">所有项目</el-menu-item>
      </el-menu>
    </div>
    <div class="header-right">
      <el-dropdown trigger="click">
        <span class="user-info">
          <el-avatar :size="32" class="user-avatar">
            {{ displayName.charAt(0).toUpperCase() }}
          </el-avatar>
          <span class="user-name">{{ displayName }}</span>
          <el-icon class="el-icon--right"><arrow-down /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item disabled>
              <span class="role-label">{{ roleLabel }}</span>
            </el-dropdown-item>
            <el-dropdown-item divided @click="goToProfile">
              个人设置
            </el-dropdown-item>
            <el-dropdown-item v-if="isOwner" @click="goToUserManage">
              用户管理
            </el-dropdown-item>
            <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-header>
</template>

<script lang="ts">
import { ArrowDown } from '@element-plus/icons-vue'
export default {
  components: { ArrowDown }
}
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
}

.app-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  cursor: pointer;
}

.app-title:hover {
  color: #409eff;
}

.header-menu {
  margin-left: 24px;
  border-bottom: none;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.user-name {
  margin-left: 8px;
  font-size: 14px;
  color: #606266;
}

.role-label {
  font-size: 12px;
  color: #909399;
}
</style>
