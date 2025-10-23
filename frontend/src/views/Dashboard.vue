<template>
  <div class="dashboard-container">
    <!-- Welcome Header -->
    <div class="dashboard-header card">
      <div class="header-content">
        <div>
          <h1>Welcome back, {{ user?.full_name || user?.email }}!</h1>
          <p class="header-subtitle">Ready to accelerate your learning journey?</p>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-number">{{ assignments.length }}</span>
            <span class="stat-label">Assignments</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ progressSummary?.average_quality_score?.toFixed(1) || '0.0' }}</span>
            <span class="stat-label">Avg Score</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions card">
      <h2>Quick Actions</h2>
      <div class="actions-grid">
        <router-link to="/assignments" class="action-card">
          <Upload class="action-icon" />
          <div class="action-content">
            <h3>Upload Assignment</h3>
            <p>Submit your homework for AI analysis</p>
          </div>
        </router-link>

        <router-link to="/assignments" class="action-card">
          <FileText class="action-icon" />
          <span class="notification-badge" v-if="assignments.length > 0">
            {{ assignments.filter(a => a.status === 'completed').length }}
          </span>
          <div class="action-content">
            <h3>View Analysis</h3>
            <p>Review your assignment feedback</p>
          </div>
        </router-link>

        <router-link to="/knowledge" class="action-card">
          <Brain class="action-icon" />
          <div class="action-content">
            <h3>Knowledge Base</h3>
            <p>Ask questions and explore concepts</p>
          </div>
        </router-link>

        <router-link to="/chat" class="action-card">
          <MessageCircle class="action-icon" />
          <div class="action-content">
            <h3>AI Chat</h3>
            <p>Interactive learning assistant</p>
          </div>
        </router-link>

        <router-link to="/profile" class="action-card">
          <User class="action-icon" />
          <div class="action-content">
            <h3>Profile</h3>
            <p>Manage your account settings</p>
          </div>
        </router-link>
      </div>
    </div>

    <!-- Recent Assignments -->
    <div class="recent-assignments card grid-item" v-if="assignments.length > 0">
      <div class="section-header">
        <h2>Recent Assignments</h2>
        <router-link to="/assignments" class="view-all-link">View All</router-link>
      </div>

      <div class="assignments-list">
        <div
          v-for="assignment in recentAssignments"
          :key="assignment.id"
          class="assignment-item"
          @click="$router.push(`/assignments/${assignment.id}`)"
        >
          <div class="assignment-info">
            <h4>{{ assignment.title }}</h4>
            <p class="assignment-date">
              {{ new Date(assignment.created_at).toLocaleDateString() }}
            </p>
          </div>

          <div class="assignment-status">
            <n-tag
              :type="getStatusType(assignment.status)"
              size="small"
            >
              {{ assignment.status }}
            </n-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- Progress Overview -->
    <div class="progress-overview card" v-if="progressSummary">
      <h2>Learning Progress</h2>

      <div class="progress-stats">
        <div class="progress-metric">
          <div class="metric-chart">
            <div class="progress-circle">
              <span class="progress-value">{{ progressSummary.average_quality_score.toFixed(1) }}</span>
              <span class="progress-max">/10</span>
            </div>
          </div>
          <div class="metric-info">
            <h3>Average Score</h3>
            <p>{{ progressSummary.overall_performance }}</p>
          </div>
        </div>

        <div class="performance-breakdown">
          <h4>Top Performers</h4>
          <div v-for="summary in progressSummary.progress_summary.slice(0, 3)" :key="summary.assignment_id" class="performance-item">
            <span class="subject">{{ summary.title }}</span>
            <n-progress
              :percentage="summary.quality_score * 10"
              :show-indicator="false"
              :border-radius="4"
              :height="8"
            />
            <span class="score">{{ summary.quality_score }}/10</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Getting Started (for new users) -->
    <div class="getting-started card" v-if="assignments.length === 0">
      <h2>Getting Started</h2>
      <div class="steps">
        <div class="step">
          <div class="step-number">1</div>
          <div class="step-content">
            <h3>Upload Your First Assignment</h3>
            <p>Take a photo of your homework or test and upload it for analysis.</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h3>Get AI Analysis</h3>
            <p>Our multimodal AI will analyze your work and provide detailed feedback.</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h3>Track Your Progress</h3>
            <p>Monitor your improvement over time and focus on areas needing attention.</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">4</div>
          <div class="step-content">
            <h3>Explore Knowledge</h3>
            <p>Use our knowledge base to deepen your understanding of concepts.</p>
          </div>
        </div>
      </div>

      <div class="cta-container">
        <router-link to="/assignments" class="btn-primary">
          Start Your First Assignment
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Upload, FileText, Brain, User, MessageCircle } from 'lucide-vue-next'
import { api } from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user)
const assignments = ref([])
const progressSummary = ref(null)
const loading = ref(false)

// Get recent assignments (last 5)
const recentAssignments = computed(() => assignments.value.slice(0, 5))

const getStatusType = (status: string) => {
  switch (status) {
    case 'completed': return 'success'
    case 'processing': return 'warning'
    case 'failed': return 'error'
    default: return 'default'
  }
}

const loadDashboardData = async () => {
  loading.value = true
  try {
    // Load assignments
    const assignmentsResponse = await api.get('/assignments/')
    assignments.value = assignmentsResponse.data

    // Load progress summary
    const progressResponse = await api.get('/assignments/progress/summary')
    progressSummary.value = progressResponse.data
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.dashboard-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* PC-optimized layout with two-column design for large screens */
@media (min-width: 1024px) {
  .dashboard-container {
    max-width: 1400px;
    padding: 0 2rem;
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(0, 1fr);
    gap: 2.5rem;
  }

  .dashboard-header {
    grid-column: 1 / -1;
  }

  .quick-actions {
    grid-column: 1;
    margin-bottom: 0;
  }

  .grid-item {
    grid-column: 2;
    margin-bottom: 0;
  }

  .progress-overview {
    grid-column: 1 / -1;
  }

  .assignments-list {
    max-height: 400px;
    overflow-y: auto;
  }
}

@media (min-width: 1400px) {
  .dashboard-container {
    max-width: 1600px;
    padding: 0 3rem;
  }
}

/* Dashboard Header */
.dashboard-header {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(59, 130, 246, 0.1));
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.header-content h1 {
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
}

.header-subtitle {
  margin: 0;
  color: var(--text-secondary);
  font-size: 1rem;
}

.header-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
}

.stat-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

/* Quick Actions */
.quick-actions h2 {
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
  font-weight: 600;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.2s;
  position: relative;
}

.action-card:hover {
  border-color: var(--primary-color);
  background: rgba(16, 185, 129, 0.1);
  transform: translateY(-2px);
}

.action-icon {
  width: 2rem;
  height: 2rem;
  color: var(--primary-color);
  flex-shrink: 0;
}

.action-content h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.action-content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.notification-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
}

/* Recent Assignments */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.view-all-link {
  color: var(--primary-color);
  text-decoration: none;
  font-size: 0.9rem;
}

.view-all-link:hover {
  text-decoration: underline;
}

.assignments-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.assignment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.assignment-item:hover {
  border-color: var(--primary-hover);
  background: rgba(16, 185, 129, 0.05);
}

.assignment-info h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.assignment-date {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* Progress Overview */
.progress-stats {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
  align-items: start;
}

.progress-metric {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.metric-chart {
  flex-shrink: 0;
}

.progress-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  box-shadow: var(--shadow-md);
}

.progress-value {
  font-size: 1.2rem;
  line-height: 1;
}

.progress-max {
  font-size: 0.7rem;
  opacity: 0.8;
}

.metric-info h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.metric-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.performance-breakdown h4 {
  margin-bottom: 1rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.performance-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.subject {
  min-width: 120px;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
}

.score {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-secondary);
  min-width: 35px;
}

/* Getting Started */
.steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.step {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.step-number {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.step-content h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.step-content p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.cta-container {
  text-align: center;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1.5rem;
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }

  .progress-stats {
    grid-template-columns: 1fr;
  }

  .steps {
    grid-template-columns: 1fr;
  }

  .assignment-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>