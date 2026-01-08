/**
 * 项目相关API
 */
import { get, post, put, del } from './request'
import type {
  Project,
  ProjectDetail,
  ProjectCreateRequest,
  ProjectUpdateRequest
} from '@/types'

/**
 * 创建项目
 * @param data - 项目创建数据
 */
export function createProject(data: ProjectCreateRequest): Promise<Project> {
  return post<Project>('/projects', data)
}

/**
 * 获取项目列表
 */
export function getProjects(): Promise<Project[]> {
  return get<Project[]>('/projects')
}

/**
 * 获取项目详情
 * @param projectId - 项目ID
 */
export function getProject(projectId: number): Promise<ProjectDetail> {
  return get<ProjectDetail>(`/projects/${projectId}`)
}

/**
 * 更新项目
 * @param projectId - 项目ID
 * @param data - 项目更新数据
 */
export function updateProject(
  projectId: number,
  data: ProjectUpdateRequest
): Promise<Project> {
  return put<Project>(`/projects/${projectId}`, data)
}

/**
 * 删除项目
 * @param projectId - 项目ID
 */
export function deleteProject(projectId: number): Promise<void> {
  return del<void>(`/projects/${projectId}`)
}
