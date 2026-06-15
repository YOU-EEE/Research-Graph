import { apiClient } from './client'

// ---------- Dashboard ----------
export function getDashboard() {
  return apiClient.get('/dashboard')
}

// ---------- Projects ----------
export function listProjects() {
  return apiClient.get('/projects')
}

export function getProject(id) {
  return apiClient.get(`/projects/${id}`)
}

export function createProject(data) {
  return apiClient.post('/projects', data)
}

export function updateProject(id, data) {
  return apiClient.put(`/projects/${id}`, data)
}

export function deleteProject(id) {
  return apiClient.delete(`/projects/${id}`)
}

// ---------- Members ----------
export function listMembers(projectId) {
  return apiClient.get(`/projects/${projectId}/members`)
}

export function addMember(projectId, data) {
  return apiClient.post(`/projects/${projectId}/members`, data)
}

export function updateMemberRole(projectId, userId, data) {
  return apiClient.put(`/projects/${projectId}/members/${userId}`, data)
}

export function removeMember(projectId, userId) {
  return apiClient.delete(`/projects/${projectId}/members/${userId}`)
}

// ---------- Tasks ----------
export function listTasks(params = {}) {
  return apiClient.get('/tasks', { params })
}

export function getTask(id) {
  return apiClient.get(`/tasks/${id}`)
}

export function createTask(data) {
  return apiClient.post('/tasks', data)
}

export function updateTask(id, data) {
  return apiClient.put(`/tasks/${id}`, data)
}

export function deleteTask(id) {
  return apiClient.delete(`/tasks/${id}`)
}

export function updateTaskStatus(id, data) {
  return apiClient.put(`/tasks/${id}/status`, data)
}

// ---------- Comments ----------
export function createComment(data) {
  return apiClient.post('/comments', data)
}

export function listComments(params = {}) {
  return apiClient.get('/comments', { params })
}

// ---------- Activity Logs ----------
export function listActivityLogs(params = {}) {
  return apiClient.get('/activity-logs', { params })
}
