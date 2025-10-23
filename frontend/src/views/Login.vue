<template>
  <div class="login-container">
    <div class="login-card card">
      <div class="login-header">
        <h1 class="login-title">Welcome Back</h1>
        <p class="login-subtitle">Sign in to continue your learning journey</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <n-form-item label="Email" :show-feedback="false">
            <n-input
              v-model:value="form.email"
              placeholder="Enter your email"
              :status="emailError ? 'error' : undefined"
              @input="clearErrors"
            />
          </n-form-item>
          <div v-if="emailError" class="error-message">{{ emailError }}</div>
        </div>

        <div class="form-group">
          <n-form-item label="Password" :show-feedback="false">
            <n-input
              v-model:value="form.password"
              type="password"
              placeholder="Enter your password"
              :status="passwordError ? 'error' : undefined"
              @input="clearErrors"
              @keydown.enter="handleLogin"
            />
          </n-form-item>
          <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
        </div>

        <n-button
          type="primary"
          size="large"
          :loading="loading"
          block
          @click="handleLogin"
          class="login-btn"
        >
          {{ loading ? 'Signing In...' : 'Sign In' }}
        </n-button>
      </form>

      <div class="login-footer">
        <p>Don't have an account?
          <router-link to="/register" class="register-link">Create one here</router-link>
        </p>
      </div>
    </div>

    <!-- Background decoration -->
    <div class="login-bg-decoration">
      <div class="decoration-circle circle-1"></div>
      <div class="decoration-circle circle-2"></div>
      <div class="decoration-circle circle-3"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  email: '',
  password: ''
})

const loading = ref(false)
const emailError = ref('')
const passwordError = ref('')

const validateForm = () => {
  let isValid = true
  emailError.value = ''
  passwordError.value = ''

  const email = form.email?.trim?.() || ''
  const password = form.password?.trim?.() || ''

  if (!email) {
    emailError.value = 'Email is required'
    isValid = false
  } else if (!/\S+@\S+\.\S+/.test(email)) {
    emailError.value = 'Please enter a valid email'
    isValid = false
  }

  if (!password) {
    passwordError.value = 'Password is required'
    isValid = false
  }

  return isValid
}

const clearErrors = () => {
  emailError.value = ''
  passwordError.value = ''
}

const handleLogin = async () => {
  if (!validateForm()) return

  loading.value = true

  try {
    const success = await authStore.login(form.email, form.password)

    if (success) {
      // Show success message
      if (window.$message) {
        window.$message.success('Login successful!')
      }

      // Redirect to dashboard
      router.push('/dashboard')
    } else {
      // Show error message
      if (window.$message) {
        window.$message.error('Login failed. Please check your credentials.')
      }
    }
  } catch (error) {
    console.error('Login error:', error)
    if (window.$message) {
      window.$message.error('An error occurred during login. Please try again.')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

.login-card {
  width: 100%;
  max-width: 400px;
  z-index: 10;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #10B981, #3B82F6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-subtitle {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.login-btn {
  margin-top: 1rem;
  background: linear-gradient(135deg, #10B981, #3B82F6);
  border: none;
  font-weight: 600;
}

.login-footer {
  text-align: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-color);
}

.register-link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.register-link:hover {
  color: var(--primary-hover);
  text-decoration: underline;
}

.error-message {
  color: var(--error-color);
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

/* Background decorations */
.login-bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.1) 0%, transparent 70%);
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: 10%;
  left: -10%;
  animation: float 6s ease-in-out infinite;
}

.circle-2 {
  width: 200px;
  height: 200px;
  top: 60%;
  right: -10%;
  animation: float 8s ease-in-out infinite reverse;
}

.circle-3 {
  width: 150px;
  height: 150px;
  bottom: 20%;
  left: 20%;
  animation: float 10s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

@media (max-width: 480px) {
  .login-container {
    padding: 1rem;
    align-items: flex-start;
    padding-top: 20vh;
  }

  .circle-1, .circle-2, .circle-3 {
    display: none;
  }
}
</style>