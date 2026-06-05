import axios from 'axios'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 12000,
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error.response?.data?.detail
    error.userMessage = Array.isArray(detail)
      ? detail.map((item) => item.msg).join('; ')
      : detail || error.message || 'Request failed'
    return Promise.reject(error)
  },
)
