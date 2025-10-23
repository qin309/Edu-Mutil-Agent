import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/services/api'

interface User {
  id: number
  email: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
}

interface AuthState {
  user: User | null
  token: string | null
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // Actions
  const setAuth = (userData: User, authToken: string) => {
    user.value = userData
    token.value = authToken

    // Store in localStorage
    localStorage.setItem('eduagent_token', authToken)
    localStorage.setItem('eduagent_user', JSON.stringify(userData))

    // Set axios default header
    if (api.defaults.headers) {
      api.defaults.headers.common['Authorization'] = `Bearer ${authToken}`
    }
  }

  const clearAuth = () => {
    user.value = null
    token.value = null

    // Clear localStorage
    localStorage.removeItem('eduagent_token')
    localStorage.removeItem('eduagent_user')

    // Remove axios header
    if (api.defaults.headers) {
      delete api.defaults.headers.common['Authorization']
    }
  }

  const checkAuth = () => {
    const storedToken = localStorage.getItem('eduagent_token')
    const storedUser = localStorage.getItem('eduagent_user')

    if (storedToken && storedUser) {
      try {
        const userData = JSON.parse(storedUser)
        user.value = userData
        token.value = storedToken

        if (api.defaults.headers) {
          api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
        }
      } catch (error) {
        clearAuth()
      }
    }
  }

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await api.post('/auth/test-login', {
        email: email,
        password: password
      })

      const { access_token, token_type, user_id, email: userEmail, role, name } = response.data

      // Construct user object from login response
      const userData = {
        id: user_id,
        email: userEmail,
        full_name: name,
        is_active: true,
        is_superuser: role === 'admin'
      }

      setAuth(userData, access_token)
      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    }
  }

  const register = async (
    email: string,
    password: string,
    confirmPassword: string,
    fullName?: string
  ): Promise<boolean> => {
    try {
      await api.post('/auth/register', {
        email,
        password,
        confirm_password: confirmPassword,
        full_name: fullName
      })
      return true
    } catch (error) {
      console.error('Registration failed:', error)
      return false
    }
  }

  const logout = () => {
    clearAuth()
  }

  const updateProfile = async (userData: Partial<User>): Promise<boolean> => {
    try {
      const response = await api.put('/v1/users/me', userData)
      if (user.value) {
        user.value = { ...user.value, ...response.data }
        localStorage.setItem('eduagent_user', JSON.stringify(user.value))
      }
      return true
    } catch (error) {
      console.error('Profile update failed:', error)
      return false
    }
  }

  // Initialize auth on store creation
  checkAuth()

  return {
    // State
    user,
    token,

    // Getters
    isAuthenticated,

    // Actions
    setAuth,
    clearAuth,
    checkAuth,
    login,
    register,
    logout,
    updateProfile
  }
})