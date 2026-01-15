<script setup lang="ts">
/**
 * 评论区组件
 * 包含评论列表和评论输入
 */
import { ref, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores'
import * as commentApi from '@/api/comment'
import type { Comment } from '@/types'

const props = defineProps<{
  taskId: number
  readonly?: boolean
}>()

const authStore = useAuthStore()
const comments = ref<Comment[]>([])
const loading = ref(false)
const submitting = ref(false)
const newComment = ref('')

const currentUserId = computed(() => authStore.currentUser?.id)

/**
 * 加载评论列表
 */
async function loadComments() {
  if (!props.taskId) return
  loading.value = true
  try {
    comments.value = await commentApi.getComments(props.taskId)
  } catch {
    ElMessage.error('加载评论失败')
  } finally {
    loading.value = false
  }
}

/**
 * 提交评论
 */
async function submitComment() {
  const content = newComment.value.trim()
  if (!content) {
    ElMessage.warning('评论内容不能为空')
    return
  }

  submitting.value = true
  try {
    const comment = await commentApi.createComment(props.taskId, { content })
    comments.value.unshift(comment)
    newComment.value = ''
    ElMessage.success('评论已添加')
  } catch {
    ElMessage.error('添加评论失败')
  } finally {
    submitting.value = false
  }
}

/**
 * 删除评论
 */
async function handleDelete(comment: Comment) {
  try {
    await ElMessageBox.confirm('确定要删除这条评论吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await commentApi.deleteComment(comment.id)
    comments.value = comments.value.filter((c) => c.id !== comment.id)
    ElMessage.success('评论已删除')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除评论失败')
    }
  }
}

/**
 * 格式化时间
 */
function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

/**
 * 获取用户显示名称
 */
function getUserDisplayName(comment: Comment): string {
  return comment.user.display_name || comment.user.username
}

// 监听 taskId 变化，重新加载评论
watch(
  () => props.taskId,
  (newId) => {
    if (newId) {
      loadComments()
    }
  },
  { immediate: true }
)
</script>

<template>
  <div class="comment-section">
    <h4 class="section-title">评论</h4>

    <!-- 评论输入 -->
    <div v-if="!readonly" class="comment-input">
      <el-input
        v-model="newComment"
        type="textarea"
        :rows="2"
        placeholder="添加评论..."
        :disabled="submitting"
      />
      <el-button
        type="primary"
        size="small"
        :loading="submitting"
        :disabled="!newComment.trim()"
        @click="submitComment"
      >
        发送
      </el-button>
    </div>

    <!-- 评论列表 -->
    <div v-loading="loading" class="comment-list">
      <div v-if="comments.length === 0 && !loading" class="empty-tip">
        暂无评论
      </div>
      <div v-for="comment in comments" :key="comment.id" class="comment-item">
        <div class="comment-header">
          <span class="comment-author">{{ getUserDisplayName(comment) }}</span>
          <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
          <el-button
            v-if="comment.user_id === currentUserId && !readonly"
            :icon="Delete"
            text
            size="small"
            class="delete-btn"
            @click="handleDelete(comment)"
          />
        </div>
        <div class="comment-content">{{ comment.content }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.comment-section {
  margin-top: 16px;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
}

.comment-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.comment-input .el-button {
  align-self: flex-end;
}

.comment-list {
  max-height: 300px;
  overflow-y: auto;
}

.empty-tip {
  text-align: center;
  color: #909399;
  padding: 16px 0;
}

.comment-item {
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.comment-author {
  font-weight: 500;
  color: #303133;
}

.comment-time {
  font-size: 12px;
  color: #909399;
}

.delete-btn {
  margin-left: auto;
  color: #909399;
}

.delete-btn:hover {
  color: #f56c6c;
}

.comment-content {
  color: #606266;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
