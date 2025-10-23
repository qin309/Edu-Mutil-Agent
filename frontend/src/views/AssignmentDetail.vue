<template>
  <div class="assignment-detail-container">
    <div v-if="loading" class="loading-state">
      <n-spin size="large" />
      <p>Loading assignment details...</p>
    </div>

    <div v-else-if="!assignment" class="error-state">
      <n-result
        status="404"
        title="Assignment Not Found"
        description="The assignment you're looking for doesn't exist or you don't have access to it."
      >
        <template #footer>
          <router-link to="/assignments" class="btn-primary">
            Back to Assignments
          </router-link>
        </template>
      </n-result>
    </div>

    <div v-else class="assignment-detail">
      <!-- Assignment Header -->
      <div class="assignment-header card">
        <div class="header-content">
          <div class="assignment-info">
            <h1>{{ assignment.title }}</h1>
            <div class="assignment-meta">
              <span class="meta-item">
                <n-icon size="16">
                  <Calendar />
                </n-icon>
                {{ formatDate(assignment.created_at) }}
              </span>
              <span v-if="assignment.original_filename" class="meta-item">
                <n-icon size="16">
                  <FileText />
                </n-icon>
                {{ assignment.original_filename }}
              </span>
              <n-tag :type="getStatusType(assignment.status)" size="small">
                {{ assignment.status }}
              </n-tag>
            </div>
          </div>
          <div class="header-actions">
            <n-button
              type="primary"
              @click="downloadFile('corrected')"
              :disabled="!assignment.corrected_filename"
            >
              Download Corrected
            </n-button>
          </div>
        </div>
      </div>

      <!-- Assignment Images -->
      <div class="images-section">
        <div class="images-grid">
          <div v-if="assignment.original_filename" class="image-card card">
            <h3>Original Image</h3>
            <div class="image-container">
              <img
                :src="getImageUrl('original')"
                alt="Original assignment"
                @load="originalImageLoaded = true"
                @error="originalImageError = true"
              />
              <div v-if="!originalImageLoaded && !originalImageError" class="image-loading">
                <n-spin />
              </div>
              <div v-if="originalImageError" class="image-error">
                Failed to load image
              </div>
            </div>
          </div>

          <div v-if="assignment.corrected_filename" class="image-card card">
            <h3>Corrected Image</h3>
            <div class="image-container">
              <img
                :src="getImageUrl('corrected')"
                alt="Corrected assignment"
                @load="correctedImageLoaded = true"
                @error="correctedImageError = true"
              />
              <div v-if="!correctedImageLoaded && !correctedImageError" class="image-loading">
                <n-spin />
              </div>
              <div v-if="correctedImageError" class="image-error">
                Failed to load image
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Analysis Results -->
      <div v-if="assignment.analysis_results" class="analysis-section card">
        <div class="section-header">
          <h2>AI Analysis Results</h2>
          <n-button
            size="small"
            @click="reanalyzeAssignment"
            :loading="reanalyzing"
          >
            Re-analyze
          </n-button>
        </div>

        <div v-if="!parsedAnalysis" class="analysis-loading">
          <n-spin />
          <p>Processing analysis data...</p>
        </div>

        <div v-else class="analysis-content">
          <!-- Analysis Overview -->
          <div class="analysis-overview">
            <div class="overview-stats">
              <div class="stat-card">
                <div class="stat-value">{{ getAnalysisScore() }}/10</div>
                <div class="stat-label">Solution Quality</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ getKnowledgePoints().length }}</div>
                <div class="stat-label">Knowledge Points</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ getErrorCount() }}</div>
                <div class="stat-label">Errors Found</div>
              </div>
            </div>
          </div>

          <!-- Detailed Analysis -->
          <div v-if="parsedAnalysis.doc_correction" class="analysis-subsection">
            <h3>Document Processing</h3>
            <div class="correction-info">
              <n-tag :type="parsedAnalysis.doc_correction.success ? 'success' : 'error'">
                {{ parsedAnalysis.doc_correction.success ? 'Document corrected' : 'No correction applied' }}
              </n-tag>
              <span v-if="parsedAnalysis.doc_correction.skew_angle !== 0" class="correction-detail">
                Skew angle: {{ parsedAnalysis.doc_correction.skew_angle.toFixed(2) }}°
              </span>
            </div>
          </div>

          <div v-if="parsedAnalysis.multimodal_analysis?.success" class="analysis-subsection">
            <h3>Content Analysis</h3>
            <div class="analysis-details">
              <div v-if="parsedAnalysis.multimodal_analysis.analysis?.subject" class="detail-row">
                <strong>Subject:</strong> {{ parsedAnalysis.multimodal_analysis.analysis.subject }}
              </div>
              <div v-if="parsedAnalysis.multimodal_analysis.analysis?.topics?.length" class="detail-row">
                <strong>Topics Covered:</strong>
                <div class="topics-list">
                  <n-tag
                    v-for="topic in parsedAnalysis.multimodal_analysis.analysis.topics"
                    :key="topic"
                    size="small"
                    type="info"
                  >
                    {{ topic }}
                  </n-tag>
                </div>
              </div>

              <div v-if="parsedAnalysis.multimodal_analysis.analysis?.knowledge_points?.length" class="detail-row">
                <strong>Knowledge Points Demonstrated:</strong>
                <ul class="knowledge-points">
                  <li v-for="point in parsedAnalysis.multimodal_analysis.analysis.knowledge_points.slice(0, 10)" :key="point">
                    {{ point }}
                  </li>
                  <li v-if="parsedAnalysis.multimodal_analysis.analysis.knowledge_points.length > 10">
                    ...and {{ parsedAnalysis.multimodal_analysis.analysis.knowledge_points.length - 10 }} more
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div v-if="parsedAnalysis.multimodal_analysis?.analysis?.common_errors?.length" class="analysis-subsection">
            <h3>Common Errors & Issues</h3>
            <div class="errors-list">
              <div
                v-for="error in parsedAnalysis.multimodal_analysis.analysis.common_errors"
                :key="error"
                class="error-item"
              >
                <n-icon size="16" color="var(--error-color)">
                  <AlertTriangle />
                </n-icon>
                {{ error }}
              </div>
            </div>
          </div>

          <div v-if="parsedAnalysis.multimodal_analysis?.analysis?.knowledge_gaps?.length" class="analysis-subsection">
            <h3>Knowledge Gaps & Recommendations</h3>
            <div class="gaps-list">
              <div
                v-for="gap in parsedAnalysis.multimodal_analysis.analysis.knowledge_gaps"
                :key="gap"
                class="gap-item"
              >
                <n-icon size="16" color="var(--warning-color)">
                  <Target />
                </n-icon>
                {{ gap }}
              </div>
            </div>
          </div>

          <div v-if="parsedAnalysis.multimodal_analysis?.analysis?.improvement_suggestions?.length" class="analysis-subsection">
            <h3>Improvement Suggestions</h3>
            <div class="suggestions-list">
              <div
                v-for="suggestion in parsedAnalysis.multimodal_analysis.analysis.improvement_suggestions"
                :key="suggestion"
                class="suggestion-item"
              >
                <n-icon size="16" color="var(--success-color)">
                  <CheckCircle />
                </n-icon>
                {{ suggestion }}
              </div>
            </div>
          </div>

          <div v-if="parsedAnalysis.multimodal_analysis?.analysis?.overall_assessment" class="analysis-subsection">
            <h3>Overall Assessment</h3>
            <div class="assessment-text">
              {{ parsedAnalysis.multimodal_analysis.analysis.overall_assessment }}
            </div>
          </div>
        </div>
      </div>

      <!-- Processing State -->
      <div v-else-if="assignment.status === 'processing'" class="processing-section card">
        <div class="processing-content">
          <n-icon size="48" color="var(--primary-color)">
            <Brain />
          </n-icon>
          <h3>AI Analysis In Progress</h3>
          <p>Your assignment is being analyzed by our AI system. This may take a few moments.</p>
          <n-progress
            type="line"
            :percentage="50"
            :show-indicator="false"
            color="var(--primary-color)"
          />
        </div>
      </div>

      <!-- Empty Analysis State -->
      <div v-else class="empty-analysis card">
        <div class="empty-content">
          <n-icon size="48" color="var(--text-muted)">
            <FileSearch />
          </n-icon>
          <h3>No Analysis Yet</h3>
          <p>Analysis results will appear here once processing is complete.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Calendar,
  FileText,
  Brain,
  AlertTriangle,
  Target,
  CheckCircle,
  FileSearch
} from 'lucide-vue-next'
import { api } from '@/services/api'

interface Assignment {
  id: number
  title: string
  original_filename?: string
  corrected_filename?: string
  status: string
  created_at: string
  analysis_results?: string
}

const route = useRoute()
const router = useRouter()
const assignment = ref<Assignment | null>(null)
const loading = ref(true)
const parsedAnalysis = ref<any>(null)
const originalImageLoaded = ref(false)
const originalImageError = ref(false)
const correctedImageLoaded = ref(false)
const correctedImageError = ref(false)
const reanalyzing = ref(false)

const assignmentId = Number(route.params.id)

const getStatusType = (status: string) => {
  switch (status) {
    case 'completed': return 'success'
    case 'processing': return 'warning'
    case 'failed': return 'error'
    default: return 'default'
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const getImageUrl = (type: 'original' | 'corrected') => {
  return `${api.defaults.baseURL}/assignments/${assignmentId}/file/${type}`
}

const downloadFile = async (type: string) => {
  try {
    const response = await api.get(`/assignments/${assignmentId}/file/${type}`, {
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${assignment.value?.title || 'assignment'}_${type}.jpg`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error) {
    console.error('Download failed:', error)
    if (window.$message) {
      window.$message.error('Failed to download file')
    }
  }
}

const getAnalysisScore = () => {
  return parsedAnalysis.value?.multimodal_analysis?.analysis?.solution_quality || 'N/A'
}

const getKnowledgePoints = (): string[] => {
  return parsedAnalysis.value?.multimodal_analysis?.analysis?.knowledge_points || []
}

const getErrorCount = (): number => {
  return parsedAnalysis.value?.multimodal_analysis?.analysis?.common_errors?.length || 0
}

const parseAnalysisResults = (analysisString: string) => {
  try {
    return JSON.parse(analysisString)
  } catch (error) {
    console.error('Failed to parse analysis results:', error)
    return null
  }
}

const reanalyzeAssignment = async () => {
  reanalyzing.value = true
  try {
    const response = await api.post(`/assignments/${assignmentId}/reanalyze`)

    if (window.$message) {
      window.$message.success('Re-analysis started. Refresh the page in a few moments.')
    }

    // Reload assignment data
    await loadAssignment()

  } catch (error) {
    console.error('Re-analysis failed:', error)
    if (window.$message) {
      window.$message.error('Failed to start re-analysis')
    }
  } finally {
    reanalyzing.value = false
  }
}

const loadAssignment = async () => {
  try {
    const response = await api.get(`/assignments/${assignmentId}`)
    assignment.value = response.data.assignment

    if (assignment.value?.analysis_results) {
      parsedAnalysis.value = parseAnalysisResults(assignment.value.analysis_results)
    }
  } catch (error) {
    console.error('Failed to load assignment:', error)
    assignment.value = null
  } finally {
    loading.value = false
  }
}

watch(() => route.params.id, async (newId) => {
  const newAssignmentId = Number(newId)
  if (newAssignmentId && newAssignmentId !== assignmentId) {
    loading.value = true
    await loadAssignment()
  }
})

onMounted(() => {
  loadAssignment()
})
</script>

<style scoped>
.assignment-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.empty-content {
  text-align: center;
  padding: 2rem;
}

.assignment-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
}

.assignment-info h1 {
  margin: 0 0 1rem 0;
  font-size: 2rem;
  font-weight: 700;
}

.assignment-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.images-section {
  margin-bottom: 2rem;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.image-card h3 {
  margin-bottom: 1rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.image-container {
  position: relative;
  background: var(--dark-bg);
  border-radius: var(--radius-md);
  padding: 1rem;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-container img {
  max-width: 100%;
  max-height: 400px;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-md);
}

.image-loading, .image-error {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: var(--text-secondary);
}

.analysis-section {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.analysis-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
  text-align: center;
}

.analysis-overview {
  margin-bottom: 2rem;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: rgba(30, 41, 59, 0.5);
  padding: 1.5rem;
  border-radius: var(--radius-lg);
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.analysis-subsection {
  margin-bottom: 2rem;
}

.analysis-subsection h3 {
  margin-bottom: 1rem;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary);
}

.correction-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.correction-detail {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.detail-row {
  margin-bottom: 1rem;
}

.detail-row strong {
  color: var(--text-primary);
  margin-right: 0.5rem;
}

.topics-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.knowledge-points {
  margin-top: 0.5rem;
  padding-left: 1.5rem;
}

.knowledge-points li {
  margin-bottom: 0.25rem;
  color: var(--text-secondary);
}

.errors-list, .gaps-list, .suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.error-item, .gap-item, .suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  background: rgba(30, 41, 59, 0.3);
  border-radius: var(--radius-md);
}

.assessment-text {
  line-height: 1.6;
  color: var(--text-secondary);
}

.processing-content, .empty-analysis {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
  text-align: center;
}

.processing-content h3, .empty-analysis h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.processing-content p, .empty-analysis p {
  margin: 0;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .images-grid {
    grid-template-columns: 1fr;
  }

  .overview-stats {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>