<template>
  <div class="profile-container">
    <div class="profile-header">
      <div class="header-content">
        <h1>Profile Settings</h1>
        <p>Manage your account information and preferences</p>
      </div>
    </div>

    <!-- Profile Form -->
    <div class="profile-form card">
      <h2>Account Information</h2>
      <form @submit.prevent="handleUpdateProfile">
        <div class="form-grid">
          <div class="form-group">
            <label for="email">Email Address</label>
            <n-input
              id="email"
              v-model:value="form.email"
              placeholder="Enter your email"
              :status="emailError ? 'error' : undefined"
              :disabled="true"
            />
            <div class="field-hint">Email cannot be changed</div>
          </div>

          <div class="form-group">
            <label for="fullName">Full Name</label>
            <n-input
              id="fullName"
              v-model:value="form.fullName"
              placeholder="Enter your full name"
              :status="fullNameError ? 'error' : undefined"
              @input="clearErrors"
            />
            <div v-if="fullNameError" class="error-message">{{ fullNameError }}</div>
          </div>

          <div class="form-group">
            <label for="currentPassword">Current Password</label>
            <n-input
              id="currentPassword"
              v-model:value="passwordForm.currentPassword"
              type="password"
              placeholder="Enter current password to change"
              show-password-toggle
            />
          </div>

          <div class="form-group">
            <label for="newPassword">New Password</label>
            <n-input
              id="newPassword"
              v-model:value="passwordForm.newPassword"
              type="password"
              placeholder="Enter new password"
              :status="newPasswordError ? 'error' : undefined"
              @input="clearErrors"
              show-password-toggle
              :disabled="!passwordForm.currentPassword"
            />
            <div v-if="newPasswordError" class="error-message">{{ newPasswordError }}</div>
          </div>

          <div class="form-group">
            <label for="confirmPassword">Confirm New Password</label>
            <n-input
              id="confirmPassword"
              v-model:value="passwordForm.confirmPassword"
              type="password"
              placeholder="Confirm new password"
              :status="confirmPasswordError ? 'error' : undefined"
              @input="clearErrors"
              show-password-toggle
              :disabled="!passwordForm.currentPassword"
            />
            <div v-if="confirmPasswordError" class="error-message">{{ confirmPasswordError }}</div>
          </div>
        </div>

        <div class="form-actions">
          <n-button
            type="primary"
            size="large"
            :loading="updatingProfile"
            @click="handleUpdateProfile"
          >
            {{ updatingProfile ? 'Updating...' : 'Update Profile' }}
          </n-button>
          <n-button
            type="info"
            size="large"
            :loading="updatingPassword"
            @click="handleUpdatePassword"
            :disabled="!passwordForm.currentPassword"
          >
            {{ updatingPassword ? 'Changing...' : 'Change Password' }}
          </n-button>
        </div>
      </form>
    </div>

    <!-- Account Statistics -->
    <div v-if="userStats" class="stats-section card">
      <h2>Your Statistics</h2>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-number">{{ userStats.total_assignments }}</div>
          <div class="stat-label">Total Assignments</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ userStats.completed_assignments }}</div>
          <div class="stat-label">Completed Analysis</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ userStats.average_score?.toFixed(1) || '0.0' }}</div>
          <div class="stat-label">Average Score</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ userStats.account_age }} days</div>
          <div class="stat-label">Account Age</div>
        </div>
      </div>
    </div>

    <!-- Account Actions -->
    <div class="account-actions card">
      <h2>Danger Zone</h2>
      <div class="action-grid">
        <div class="action-item">
          <div class="action-content">
            <h3>Data Export</h3>
            <p>Download a copy of all your assignments and analysis data</p>
          </div>
          <n-button type="default" @click="handleExportData">
            Export Data
          </n-button>
        </div>

        <div class="action-item warning">
          <div class="action-content">
            <h3>Delete Account</h3>
            <p>Permanently delete your account and all associated data. This action cannot be undone.</p>
          </div>
          <n-button type="error" @click="handleDeleteAccount" :loading="deleting">
            {{ deleting ? 'Deleting...' : 'Delete Account' }}
          </n-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'

interface UserStats {
  total_assignments: number
  completed_assignments: number
  average_score: number | null
  account_age: number
}

const authStore = useAuthStore()

const form = reactive({
  email: '',
  fullName: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const updatingProfile = ref(false)
const updatingPassword = ref(false)
const deleting = ref(false)
const userStats = ref<UserStats | null>(null)

const emailError = ref('')
const fullNameError = ref('')
const newPasswordError = ref('')
const confirmPasswordError = ref('')

const user = computed(() => authStore.user)

// Load user data on mount
const loadUserData = () => {
  if (user.value) {
    form.email = user.value.email
    form.fullName = user.value.full_name || ''
  }
  loadUserStats()
}

const clearErrors = () => {
  emailError.value = ''
  fullNameError.value = ''
  newPasswordError.value = ''
  confirmPasswordError.value = ''
}

const validateProfileForm = (): boolean => {
  let isValid = true
  fullNameError.value = ''

  if (form.fullName && form.fullName.trim?.().length < 2) {
    fullNameError.value = 'Full name must be at least 2 characters'
    isValid = false
  }

  return isValid
}

const validatePasswordForm = (): boolean => {
  let isValid = true
  newPasswordError.value = ''
  confirmPasswordError.value = ''

  if (!passwordForm.currentPassword) {
    newPasswordError.value = 'Current password is required'
    isValid = false
  }

  if (!passwordForm.newPassword) {
    newPasswordError.value = 'New password is required'
    isValid = false
  } else if (passwordForm.newPassword.length < 6) {
    newPasswordError.value = 'New password must be at least 6 characters'
    isValid = false
  }

  if (!passwordForm.confirmPassword) {
    confirmPasswordError.value = 'Please confirm new password'
    isValid = false
  } else if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    confirmPasswordError.value = 'Passwords do not match'
    isValid = false
  }

  return isValid
}

const handleUpdateProfile = async () => {
  if (!validateProfileForm()) return

  updatingProfile.value = true

  try {
    const success = await authStore.updateProfile({
      full_name: form.fullName?.trim?.() || ''
    })

    if (success) {
      if (window.$message) {
        window.$message.success('Profile updated successfully!')
      }
    } else {
      throw new Error('Profile update failed')
    }
  } catch (error) {
    console.error('Profile update failed:', error)
    if (window.$message) {
      window.$message.error('Failed to update profile. Please try again.')
    }
  } finally {
    updatingProfile.value = false
  }
}

const handleUpdatePassword = async () => {
  if (!validatePasswordForm()) return

  updatingPassword.value = true

  try {
    // In a real implementation, you would have a separate password change endpoint
    // For now, we'll update the profile with a password field
    const success = await authStore.updateProfile({
      password: passwordForm.newPassword
    })

    if (success) {
      if (window.$message) {
        window.$message.success('Password changed successfully!')
      }
      // Clear password form
      passwordForm.currentPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
    } else {
      throw new Error('Password change failed')
    }
  } catch (error) {
    console.error('Password change failed:', error)
    if (window.$message) {
      window.$message.error('Failed to change password. Please try again.')
    }
  } finally {
    updatingPassword.value = false
  }
}

const loadUserStats = async () => {
  try {
    // Get statistics from various endpoints
    const assignmentsResponse = await api.get('/assignments/')
    const assignments = assignmentsResponse.data

    const createdDate = new Date(user.value.created_at)
    const accountAge = Math.floor((Date.now() - createdDate.getTime()) / (1000 * 60 * 60 * 24))

    userStats.value = {
      total_assignments: assignments.length,
      completed_assignments: assignments.filter((a: any) => a.status === 'completed').length,
      average_score: null, // Would calculate from assignment analysis scores
      account_age: accountAge
    }
  } catch (error) {
    console.error('Failed to load user stats:', error)
  }
}

const handleExportData = () => {
  // In a real implementation, this would trigger a data export
  if (window.$message) {
    window.$message.info('Data export feature coming soon!')
  }
}

const handleDeleteAccount = async () => {
  // Confirm deletion
  if (window.$dialog) {
    const result = await window.$dialog.warning({
      title: 'Delete Account',
      content: 'Are you sure you want to permanently delete your account? This action cannot be undone and all your data will be lost.',
      positiveText: 'Delete Account',
      negativeText: 'Cancel',
      onPositiveClick: async () => {
        deleting.value = true
        try {
          // In a real implementation, you'd call a delete account endpoint
          // For now, just show a message
          if (window.$message) {
            window.$message.info('Account deletion would be implemented here')
          }
        } catch (error) {
          console.error('Account deletion failed:', error)
        } finally {
          deleting.value = false
        }
      }
    })
  }
}

onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-header {
  margin-bottom: 2rem;
}

.header-content h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 700;
}

.header-content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.profile-form {
  margin-bottom: 2rem;
}

.profile-form h2 {
  margin-bottom: 2rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: var(--text-primary);
}

.field-hint {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.error-message {
  color: var(--error-color);
  font-size: 0.8rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-start;
}

.stats-section {
  margin-bottom: 2rem;
}

.stats-section h2 {
  margin-bottom: 2rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1.5rem;
}

.stat-item {
  background: rgba(30, 41, 59, 0.5);
  padding: 1.5rem;
  border-radius: var(--radius-lg);
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.account-actions {
  border: 1px solid var(--error-color);
  background: rgba(239, 68, 68, 0.05);
}

.account-actions h2 {
  margin-bottom: 2rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--error-color);
}

.action-grid {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.action-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.action-content h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.action-content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.action-item.warning .action-content h3 {
  color: var(--error-color);
}

@media (max-width: 768px) {
  .action-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .form-actions {
    flex-direction: column;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>