/**
 * 路由配置模块
 */
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        redirect: '/projects/my'
      },
      {
        path: 'projects',
        redirect: '/projects/my'
      },
      {
        path: 'projects/my',
        name: 'MyProjects',
        component: () => import('@/views/ProjectList.vue'),
        meta: { filter: 'my' }
      },
      {
        path: 'projects/all',
        name: 'AllProjects',
        component: () => import('@/views/ProjectList.vue'),
        meta: { filter: 'all' }
      },
      {
        path: 'projects/:id',
        name: 'Board',
        component: () => import('@/views/BoardView.vue')
      },
      {
        path: 'users',
        name: 'UserManage',
        component: () => import('@/views/UserManageView.vue'),
        meta: { requiresOwner: true }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/ProfileView.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

/**
 * 路由守卫
 * 使用闭包封装初始化状态，避免模块级变量在热更新时状态不一致
 */
const createAuthGuard = () => {
  let isInitializing = false
  let initPromise: Promise<void> | null = null

  return async (to: import('vue-router').RouteLocationNormalized, _from: import('vue-router').RouteLocationNormalized, next: import('vue-router').NavigationGuardNext) => {
    const authStore = useAuthStore()

    // 如果有Token但没有用户信息，尝试获取（只在首次时阻塞）
    if (authStore.token && !authStore.user) {
      // 避免重复初始化
      if (!isInitializing) {
        isInitializing = true
        initPromise = authStore.initAuth().finally(() => {
          isInitializing = false
          initPromise = null
        })
      }
      // 等待初始化完成
      if (initPromise) {
        await initPromise
      }
    }

    const requiresAuth = to.matched.some((record) => record.meta.requiresAuth !== false)
    const requiresOwner = to.matched.some((record) => record.meta.requiresOwner === true)

    if (requiresAuth && !authStore.isAuthenticated) {
      // 需要认证但未登录，跳转登录页
      next({ name: 'Login', query: { redirect: to.fullPath } })
    } else if (requiresOwner && authStore.user?.role !== 'owner') {
      // 需要所有者权限但当前用户不是所有者，跳转首页
      next({ name: 'Home' })
    } else if (!requiresAuth && authStore.isAuthenticated && (to.name === 'Login' || to.name === 'Register')) {
      // 已登录用户访问登录/注册页，跳转首页
      next({ name: 'Home' })
    } else {
      next()
    }
  }
}

router.beforeEach(createAuthGuard())

export default router
