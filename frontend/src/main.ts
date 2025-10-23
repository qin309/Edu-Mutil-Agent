import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import { createDiscreteApi } from 'naive-ui'
import naive from 'naive-ui'

import App from './App.vue'
import routes from './router'
import { useAuthStore } from './stores/auth'

import './style.css'

// Pinia store
const pinia = createPinia()

// Router
const router = createRouter({
  history: createWebHistory(),
  routes
})

// Router guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore(pinia)

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

// Global properties for Naive UI discrete APIs
const { message, notification, dialog, loadingBar } = createDiscreteApi(
  ['message', 'dialog', 'notification', 'loadingBar'],
  {
    messageProviderProps: { placement: 'top' },
    notificationProviderProps: { placement: 'top-right' }
  }
)

// Create app
const app = createApp(App)
  .use(naive)
  .use(router)
  .use(pinia)

app.config.globalProperties.$message = message
app.config.globalProperties.$notification = notification
app.config.globalProperties.$dialog = dialog
app.config.globalProperties.$loadingBar = loadingBar

// Mount app
app.mount('#app')