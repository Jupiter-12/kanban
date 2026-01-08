<script setup lang="ts">
/**
 * 应用主布局
 */
import AppHeader from './AppHeader.vue'
</script>

<template>
  <el-container class="app-layout">
    <AppHeader />
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: #f5f7fa;
}

.app-main {
  padding: 24px;
  overflow: auto;
}
</style>
