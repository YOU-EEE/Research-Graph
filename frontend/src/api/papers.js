import { API_BASE_URL, apiClient } from './client'

export function fetchPapers(params = {}) {
  return apiClient.get('/papers/', { params }).then((res) => res.data)
}

export function fetchPaper(paperId) {
  return apiClient.get(`/papers/${paperId}`).then((res) => res.data)
}

export function createPaper(payload) {
  return apiClient.post('/papers/', payload).then((res) => res.data)
}

export function updatePaper(paperId, payload) {
  return apiClient.put(`/papers/${paperId}`, payload).then((res) => res.data)
}

export function deletePaper(paperId) {
  return apiClient.delete(`/papers/${paperId}`).then((res) => res.data)
}

export function fetchAuthors() {
  return apiClient.get('/authors/').then((res) => res.data)
}

export function createAuthor(payload) {
  return apiClient.post('/authors/', payload).then((res) => res.data)
}

export function fetchTags() {
  return apiClient.get('/tags/').then((res) => res.data)
}

export function createTag(payload) {
  return apiClient.post('/tags/', payload).then((res) => res.data)
}

export function deleteTag(tagId) {
  return apiClient.delete(`/tags/${tagId}`).then((res) => res.data)
}

export function addPaperTag(paperId, payload) {
  return apiClient.post(`/papers/${paperId}/tags`, payload).then((res) => res.data)
}

export function removePaperTag(paperId, tagId) {
  return apiClient.delete(`/papers/${paperId}/tags/${tagId}`).then((res) => res.data)
}

export function fetchVenues() {
  return apiClient.get('/venues/').then((res) => res.data)
}

export function createVenue(payload) {
  return apiClient.post('/venues/', payload).then((res) => res.data)
}

export function deleteVenue(venueId) {
  return apiClient.delete(`/venues/${venueId}`).then((res) => res.data)
}

export function fetchCollections() {
  return apiClient.get('/collections/').then((res) => res.data)
}

export function createCollection(payload) {
  return apiClient.post('/collections/', payload).then((res) => res.data)
}

export function deleteCollection(collectionId) {
  return apiClient.delete(`/collections/${collectionId}`).then((res) => res.data)
}

export function fetchCollectionPapers(collectionId) {
  return apiClient.get(`/collections/${collectionId}/papers`).then((res) => res.data)
}

export function addPaperToCollection(collectionId, paperId) {
  return apiClient
    .post(`/collections/${collectionId}/papers/${paperId}`)
    .then((res) => res.data)
}

export function removePaperFromCollection(collectionId, paperId) {
  return apiClient
    .delete(`/collections/${collectionId}/papers/${paperId}`)
    .then((res) => res.data)
}

export function uploadAttachment(paperId, file) {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient
    .post(`/papers/${paperId}/attachments`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then((res) => res.data)
}

export function attachmentPreviewUrl(paperId, attachmentId) {
  return `${API_BASE_URL}/papers/${paperId}/attachments/${attachmentId}/preview`
}

export function importBibtex(rawBibtex) {
  return apiClient.post('/import/bibtex', { raw_bibtex: rawBibtex }).then((res) => res.data)
}

export function importBibtexFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient
    .post('/import/bibtex/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then((res) => res.data)
}
