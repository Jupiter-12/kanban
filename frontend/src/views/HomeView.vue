<script setup lang="ts">
/**
 * 首页视图组件
 */
import { computed } from 'vue'
import { useAuthStore } from '@/stores'

const authStore = useAuthStore()
const user = computed(() => authStore.currentUser)
</script>

<template>
  <div class="home">
    <el-card class="welcome-card">
      <h2>欢迎回来，{{ user?.display_name || user?.username }}！</h2>
      <p>这里是您的看板工作区，开始管理您的任务吧。</p>
    </el-card>
  </div>
</template>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 24px;
}

.welcome-card h2 {
  margin: 0 0 8px;
  font-size: 24px;
  color: #303133;
}

.welcome-card p {
  margin: 0;
  color: #909399;
}
</style>
