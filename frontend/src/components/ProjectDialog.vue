<script setup lang="ts">
/**
 * 项目对话框组件
 */
import { ref, watch } from 'vue'

const props = defineProps<{
  visible: boolean
  project: { id: number; name: string; description: string } | null
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  confirm: [data: { name: string; description: string }]
}>()

const form = ref({
  name: '',
  description: ''
})

const formRef = ref()

const rules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 1, max: 100, message: '项目名称长度为1-100个字符', trigger: 'blur' }
  ]
}

watch(
  () => props.visible,
  (val) => {
    if (val) {
      if (props.project) {
        form.value = {
          name: props.project.name,
          description: props.project.description
        }
      } else {
        form.value = { name: '', description: '' }
      }
    }
  }
)

function handleClose() {
  emit('update:visible', false)
  formRef.value?.resetFields()
}

async function handleConfirm() {
  try {
    await formRef.value?.validate()
    emit('confirm', { ...form.value })
    handleClose()
  } catch {
    // 验证失败
  }
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    :title="project ? '编辑项目' : '创建项目'"
    width="500px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="80px"
    >
      <el-form-item label="项目名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="请输入项目名称"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="项目描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          placeholder="请输入项目描述（可选）"
          :rows="3"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleConfirm">
        {{ project ? '保存' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>
