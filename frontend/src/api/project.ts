/**
 * 项目相关API
 */
import { get, post, put, del } from './request'
import type {
  Project,
  ProjectDetail,
  ProjectCreateRequest,
  ProjectUpdateRequest,
  TaskFilterParams
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
 * @param filter - 任务筛选参数（可选）
 */
export function getProject(
  projectId: number,
  filter?: TaskFilterParams
): Promise<ProjectDetail> {
  // 构建查询参数
  const params = new URLSearchParams()
  if (filter) {
    if (filter.keyword) params.append('keyword', filter.keyword)
    if (filter.assignee_id !== undefined && filter.assignee_id !== null)
      params.append('assignee_id', String(filter.assignee_id))
    if (filter.priority) params.append('priority', filter.priority)
    if (filter.due_date_start) params.append('due_date_start', filter.due_date_start)
    if (filter.due_date_end) params.append('due_date_end', filter.due_date_end)
  }
  const queryString = params.toString()
  const url = queryString
    ? `/projects/${projectId}?${queryString}`
    : `/projects/${projectId}`
  return get<ProjectDetail>(url)
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
