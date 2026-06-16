import { apiClient } from './client'

export function fetchNotes(params = {}) {
  return apiClient.get('/notes/', { params }).then((res) => res.data)
}

export function fetchPaperNotes(paperId) {
  return apiClient.get(`/papers/${paperId}/notes`).then((res) => res.data)
}

export function fetchNote(noteId) {
  return apiClient.get(`/notes/${noteId}`).then((res) => res.data)
}

export function createNote(payload) {
  return apiClient.post('/notes/', payload).then((res) => res.data)
}

export function updateNote(noteId, payload) {
  return apiClient.put(`/notes/${noteId}`, payload).then((res) => res.data)
}

export function deleteNote(noteId) {
  return apiClient.delete(`/notes/${noteId}`).then((res) => res.data)
}

export function parseNoteLinks(noteId) {
  return apiClient.post(`/notes/${noteId}/parse-links`).then((res) => res.data)
}

export function fetchNoteBacklinks(noteId) {
  return apiClient.get(`/notes/${noteId}/backlinks`).then((res) => res.data)
}

export function fetchConcepts(params = {}) {
  return apiClient.get('/concepts/', { params }).then((res) => res.data)
}

export function fetchConcept(conceptId) {
  return apiClient.get(`/concepts/${conceptId}`).then((res) => res.data)
}

export function fetchConceptNotes(conceptId) {
  return apiClient.get(`/concepts/${conceptId}/notes`).then((res) => res.data)
}

export function updateConcept(conceptId, payload) {
  return apiClient.put(`/concepts/${conceptId}`, payload).then((res) => res.data)
}
