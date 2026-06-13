import { apiClient } from './client'

export function login(username, password) {
  return apiClient.post('/login', { username, password })
}

export function register(username, password) {
  return apiClient.post('/register', { username, password })
}

export function getUsers() {
  return apiClient.get('/users')
}

export function getMe() {
  return apiClient.get('/me')
}
