import { apiClient } from './client'

// 云端 AI「生成」类请求较慢（需多次访问大模型），单独放长超时，覆盖全局 12s
const AI_TIMEOUT = 120000

// ---------- 自动标签推荐 ----------
export function generateTagSuggestions(paperId, mode) {
  return apiClient
    .post(`/ai/tag-suggestions/${paperId}`, null, {
      params: mode ? { mode } : {},
      timeout: AI_TIMEOUT,
    })
    .then((res) => res.data)
}

export function getTagSuggestions(paperId) {
  return apiClient.get(`/ai/tag-suggestions/${paperId}`).then((res) => res.data)
}

export function acceptTagSuggestion(suggestionId) {
  return apiClient
    .post(`/ai/tag-suggestions/${suggestionId}/accept`)
    .then((res) => res.data)
}

// ---------- 相似论文推荐 ----------
export function generateSimilarity(paperId, mode, topK) {
  const params = {}
  if (mode) params.mode = mode
  if (topK) params.top_k = topK
  return apiClient
    .post(`/ai/similarity/${paperId}`, null, { params, timeout: AI_TIMEOUT })
    .then((res) => res.data)
}

export function getSimilarity(paperId) {
  return apiClient.get(`/ai/similarity/${paperId}`).then((res) => res.data)
}

// ---------- 关系补边推荐 ----------
export function generateRelationSuggestions(paperId, mode) {
  return apiClient
    .post(`/ai/relation-suggestions/${paperId}`, null, {
      params: mode ? { mode } : {},
      timeout: AI_TIMEOUT,
    })
    .then((res) => res.data)
}

export function getRelationSuggestions(paperId) {
  return apiClient.get(`/ai/relation-suggestions/${paperId}`).then((res) => res.data)
}

export function acceptRelationSuggestion(suggestionId) {
  return apiClient
    .post(`/ai/relation-suggestions/${suggestionId}/accept`)
    .then((res) => res.data)
}

// ---------- Related Work 主题聚类 ----------
export function generateClusters(payload) {
  return apiClient
    .post('/ai/clusters', payload, { timeout: AI_TIMEOUT })
    .then((res) => res.data)
}

export function getClusters(projectId) {
  const url = projectId ? `/ai/clusters/${projectId}` : '/ai/clusters'
  return apiClient.get(url).then((res) => res.data)
}
