import axios, { AxiosInstance, AxiosResponse } from 'axios'

export const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 60000, // Increased to 60 seconds for knowledge queries
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('eduagent_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('eduagent_token')
      localStorage.removeItem('eduagent_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api