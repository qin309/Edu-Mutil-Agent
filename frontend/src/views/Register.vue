<template>
  <div class="register-container">
    <div class="register-card card">
      <div class="register-header">
        <h1 class="register-title">Join EduAgent</h1>
        <p class="register-subtitle">Create your account to start your learning journey</p>
      </div>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="fullName" class="form-label">Full Name (Optional)</label>
          <input
            id="fullName"
            v-model="form.fullName"
            type="text"
            placeholder="Enter your full name"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="email" class="form-label">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="Enter your email"
            :class="['form-input', emailError ? 'error' : '']"
            @input="clearErrors"
          />
          <div v-if="emailError" class="error-message">{{ emailError }}</div>
        </div>

        <div class="form-group">
          <label for="password" class="form-label">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="Create a password"
            :class="['form-input', passwordError ? 'error' : '']"
            @input="clearErrors"
          />
          <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
        </div>

        <div class="form-group">
          <label for="confirmPassword" class="form-label">Confirm Password</label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            type="password"
            placeholder="Confirm your password"
            :class="['form-input', confirmError ? 'error' : '']"
            @input="clearErrors"
          />
          <div v-if="confirmError" class="error-message">{{ confirmError }}</div>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="btn-primary"
        >
          {{ loading ? 'Creating Account...' : 'Create Account' }}
        </button>
      </form>

      <div class="register-footer">
        <p>Already have an account?
          <router-link to="/login" class="login-link">Sign in here</router-link>
        </p>
      </div>
    </div>

    <!-- Benefits section -->
    <div class="benefits-sidebar">
      <div class="benefit-card card">
        <h3>Why Choose EduAgent?</h3>
        <div class="benefits-list">
          <div class="benefit-item">
            <span class="benefit-icon">🚀</span>
            <div>
              <strong>Accelerated Learning</strong>
              <p>Get instant feedback on your assignments with AI-powered analysis</p>
            </div>
          </div>
          <div class="benefit-item">
            <span class="benefit-icon">🎯</span>
            <div>
              <strong>Personalized Insights</strong>
              <p>Receive tailored recommendations based on your performance</p>
            </div>
          </div>
          <div class="benefit-item">
            <span class="benefit-icon">📊</span>
            <div>
              <strong>Progress Tracking</strong>
              <p>Monitor your improvement over time with detailed analytics</p>
            </div>
          </div>
          <div class="benefit-item">
            <span class="benefit-icon">📚</span>
            <div>
              <strong>Knowledge Connections</strong>
              <p>Understand how concepts connect across your curriculum</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  fullName: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const loading = ref(false)
const emailError = ref('')
const passwordError = ref('')
const confirmError = ref('')

const validateForm = (): boolean => {
  let isValid = true
  emailError.value = ''
  passwordError.value = ''
  confirmError.value = ''

  if (!form.email) {
    emailError.value = 'Email is required'
    isValid = false
  } else if (!/\S+@\S+\.\S+/.test(form.email)) {
    emailError.value = 'Please enter a valid email'
    isValid = false
  }

  if (!form.password) {
    passwordError.value = 'Password is required'
    isValid = false
  } else if (form.password.length < 6) {
    passwordError.value = 'Password must be at least 6 characters'
    isValid = false
  }

  if (!form.confirmPassword) {
    confirmError.value = 'Please confirm your password'
    isValid = false
  } else if (form.password !== form.confirmPassword) {
    confirmError.value = 'Passwords do not match'
    isValid = false
  }

  return isValid
}

const clearErrors = () => {
  emailError.value = ''
  passwordError.value = ''
  confirmError.value = ''
}

const handleRegister = async () => {
  console.log('Registration started')
  console.log('Form data:', form)

  if (!validateForm()) {
    console.log('Form validation failed')
    return
  }

  console.log('Starting registration...')
  loading.value = true

  try {
    console.log('Making API call using auth store')
    const success = await authStore.register(
      form.email,
      form.password,
      form.confirmPassword,
      form.fullName || undefined
    )

    if (success) {
      console.log('Registration successful')

      // Show success message
      if (window.$message) {
        window.$message.success('Account created successfully!')
      }

      // Redirect to login
      router.push('/login')
    }
  } catch (error) {
    console.error('Registration error:', error)
    if (window.$message) {
      window.$message.error('Registration failed. Email might already be registered.')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 400px;
  padding: 2rem;
  gap: 2rem;
  align-items: start;
  justify-content: center;
}

.register-card {
  width: 100%;
  max-width: 400px;
  justify-self: end;
}

.register-header {
  text-align: center;
  margin-bottom: 2rem;
}

.register-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #10B981, #3B82F6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.register-subtitle {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.register-btn {
  margin-top: 1rem;
  background: linear-gradient(135deg, #10B981, #3B82F6);
  border: none;
  font-weight: 600;
}

.register-footer {
  text-align: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-color);
}

.login-link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.login-link:hover {
  color: var(--primary-hover);
  text-decoration: underline;
}

.error-message {
  color: var(--error-color);
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.benefits-sidebar {
  position: sticky;
  top: 2rem;
}

.benefit-card {
  padding: 2rem;
}

.benefit-card h3 {
  margin-bottom: 2rem;
  font-size: 1.5rem;
  font-weight: 600;
  text-align: center;
}

.benefits-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.benefit-item {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.benefit-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.benefit-item strong {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.benefit-item p {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0;
  line-height: 1.4;
}

@media (max-width: 1024px) {
  .register-container {
    grid-template-columns: 1fr;
    gap: 3rem;
  }

  .register-card {
    max-width: none;
    justify-self: center;
  }

  .benefits-sidebar {
    position: static;
  }

  .benefit-card {
    order: -1;
  }
}

@media (max-width: 480px) {
  .register-container {
    padding: 1rem;
  }
}
</style>