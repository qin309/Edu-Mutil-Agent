<template>
  <n-config-provider
    :theme="darkTheme ? darkTheme : undefined"
    :theme-overrides="themeOverrides"
  >
    <n-message-provider>
      <div id="app" class="app-container">
              <!-- Navigation Header -->
              <nav class="navbar" v-if="!isLoginPage && !isRegisterPage">
                <div class="nav-container">
                  <div class="nav-brand">
                    <h2>EduAgent</h2>
                    <span class="nav-subtitle">Multimodal Educational Assistant</span>
                  </div>

                  <div class="nav-menu" v-if="isAuthenticated">
                    <router-link to="/dashboard" class="nav-link">
                      <BookOpen class="nav-icon" />
                      Dashboard
                    </router-link>
                    <router-link to="/assignments" class="nav-link">
                      <FileText class="nav-icon" />
                      Assignments
                    </router-link>
                    <router-link to="/knowledge" class="nav-link">
                      <Brain class="nav-icon" />
                      Knowledge Base
                    </router-link>
                    <router-link to="/knowledge-graph" class="nav-link">
                      <Network class="nav-icon" />
                      Knowledge Graph
                    </router-link>
                    <router-link to="/chat" class="nav-link">
                      <MessageCircle class="nav-icon" />
                      Chat
                    </router-link>
                    <router-link to="/profile" class="nav-link">
                      <User class="nav-icon" />
                      Profile
                    </router-link>
                  </div>

                  <div class="nav-actions" v-if="isAuthenticated">
                    <n-button
                      size="small"
                      @click="handleLogout"
                      type="default"
                    >
                      Logout
                    </n-button>
                  </div>

                  <div class="nav-actions" v-else>
                    <router-link to="/login" class="nav-link login-link">
                      Login
                    </router-link>
                    <router-link to="/register" class="btn-primary nav-btn">
                      Sign Up
                    </router-link>
                  </div>
                </div>
              </nav>

              <!-- Main Content -->
              <main class="main-content">
                <router-view />
              </main>

              <!-- Footer -->
              <footer class="footer" v-if="!isLoginPage && !isRegisterPage">
                <div class="footer-content">
                  <p>&copy; 2025 EduAgent. Powered by AI for better learning.</p>
                </div>
              </footer>
    </div>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  BookOpen,
  FileText,
  Brain,
  User,
  LogOut,
  MessageCircle,
  Network
} from 'lucide-vue-next'
import { darkTheme } from 'naive-ui'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const isLoginPage = computed(() => route.name === 'Login')
const isRegisterPage = computed(() => route.name === 'Register')

const themeOverrides = {
  common: {
    primaryColor: '#10B981',
    primaryColorHover: '#059669',
    primaryColorPressed: '#047857',
    borderRadius: '8px',
    fontSize: '14px'
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  // Check authentication on app load
  authStore.checkAuth()
})
</script>

<style>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #e2e8f0;
}

.navbar {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-brand h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  background: linear-gradient(135deg, #10B981, #3B82F6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-subtitle {
  font-size: 0.75rem;
  color: #94a3b8;
  display: block;
  margin-top: 0.25rem;
}

.nav-menu {
  display: flex;
  gap: 2rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #cbd5e1;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.nav-link:hover {
  color: #10B981;
  background: rgba(16, 185, 129, 0.1);
}

.nav-link.router-link-active {
  color: #10B981;
  background: rgba(16, 185, 129, 0.2);
}

.nav-icon {
  width: 1rem;
  height: 1rem;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.login-link {
  color: var(--text-secondary) !important;
  text-decoration: none;
}

.login-link:hover {
  color: var(--primary-color) !important;
}

.nav-btn {
  padding: 0.375rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  color: white;
}

.main-content {
  flex: 1;
  padding: 50rem  2rem 2rem 2rem;
  margin-top: var(--navbar-height);
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.footer {
  margin-top: auto;
  padding: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(5px);
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #64748b;
}

.footer-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.footer-links a {
  color: #64748b;
  text-decoration: none;
}

.footer-links a:hover {
  color: #10B981;
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 1rem;
    padding: 0 1rem;
  }

  .nav-menu {
    flex-wrap: wrap;
    justify-content: center;
  }

  .main-content {
    padding: 1rem;
  }

  .footer-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
}
</style>