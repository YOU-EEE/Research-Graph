import axios from 'axios'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 12000,
})

// 请求拦截器：自动附加用户认证头
apiClient.interceptors.request.use((config) => {
  const userId = localStorage.getItem('x_user_id')
  if (userId) {
    config.headers['x-user-id'] = userId
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error.response?.data?.detail
    error.userMessage = Array.isArray(detail)
      ? detail.map((item) => item.msg).join('; ')
      : detail || error.message || 'Request failed'

    // 未认证时跳转登录页
    if (error.response?.status === 401) {
      localStorage.removeItem('user')
      localStorage.removeItem('x_user_id')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)
