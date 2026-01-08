/**
 * 项目状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Project, ProjectCreateRequest, ProjectUpdateRequest } from '@/types'
import * as projectApi from '@/api/project'

export const useProjectStore = defineStore('project', () => {
  // 状态
  const projects = ref<Project[]>([])
  const loading = ref(false)

  // 计算属性
  const projectList = computed(() => projects.value)
  const projectCount = computed(() => projects.value.length)

  /**
   * 获取项目列表
   */
  async function fetchProjects(): Promise<void> {
    loading.value = true
    try {
      projects.value = await projectApi.getProjects()
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建项目
   */
  async function createProject(data: ProjectCreateRequest): Promise<Project> {
    loading.value = true
    try {
      const project = await projectApi.createProject(data)
      projects.value.unshift(project)
      return project
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新项目
   */
  async function updateProject(
    projectId: number,
    data: ProjectUpdateRequest
  ): Promise<Project> {
    loading.value = true
    try {
      const updatedProject = await projectApi.updateProject(projectId, data)
      const index = projects.value.findIndex((p) => p.id === projectId)
      if (index !== -1) {
        projects.value[index] = updatedProject
      }
      return updatedProject
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除项目
   */
  async function deleteProject(projectId: number): Promise<void> {
    loading.value = true
    try {
      await projectApi.deleteProject(projectId)
      projects.value = projects.value.filter((p) => p.id !== projectId)
    } finally {
      loading.value = false
    }
  }

  /**
   * 根据ID获取项目
   */
  function getProjectById(projectId: number): Project | undefined {
    return projects.value.find((p) => p.id === projectId)
  }

  return {
    // 状态
    projects,
    loading,
    // 计算属性
    projectList,
    projectCount,
    // 方法
    fetchProjects,
    createProject,
    updateProject,
    deleteProject,
    getProjectById
  }
})
