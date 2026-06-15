import { apiClient } from './client'

export function getGraph(params = {}) {
  return apiClient.get('/graph', { params })
}

export function getProjectGraph(projectId) {
  return apiClient.get(`/graph/project/${projectId}`)
}

export function getPaperGraph(paperId) {
  return apiClient.get(`/graph/paper/${paperId}`)
}

export function getConceptGraph(conceptId) {
  return apiClient.get(`/graph/concept/${conceptId}`)
}
