/**
 * 应用入口文件
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus, { ElMessage } from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

// 全局错误处理
app.config.errorHandler = (err, _instance, info) => {
  console.error('全局错误:', err)
  console.error('错误信息:', info)

  // 避免重复显示已处理的 API 错误
  if (err instanceof Error && !err.message.includes('Request failed')) {
    ElMessage.error(`发生错误: ${err.message}`)
  }
}

// 未捕获的 Promise 错误处理
window.addEventListener('unhandledrejection', (event) => {
  console.error('未处理的Promise错误:', event.reason)
  // 避免重复显示已处理的 API 错误
  if (event.reason && !event.reason.response) {
    ElMessage.error('操作失败，请稍后重试')
  }
  event.preventDefault()
})

app.mount('#app')
