<template>
  <div class="assignments-container">
    <div class="assignments-header">
      <div class="header-content">
        <h1>My Assignments</h1>
        <p>Upload and manage your assignments for AI analysis</p>
      </div>
      <router-link to="/assignments" class="upload-btn btn-primary">
        Upload New Assignment
      </router-link>
    </div>

    <!-- Assignment Upload Section -->
    <div v-if="showUpload" class="upload-section card">
      <h2>Upload New Assignment</h2>
      <form @submit.prevent="handleFileUpload" class="upload-form">
        <div class="form-group">
          <label for="assignment-file">Assignment File</label>
          <n-upload
            v-model:file-list="fileList"
            multiple
            accept="image/*"
            :max="1"
            :custom-request="handleUploadRequest"
            @update:file-list="handleFileChange"
          >
            <div class="upload-area">
              <n-icon size="48" color="#10B981">
                <FileImage />
              </n-icon>
              <p class="upload-text">
                Click or drag image files here to upload
              </p>
              <p class="upload-hint">
                Supported formats: JPEG, PNG, GIF, TIFF, BMP (Max 10MB)
              </p>
            </div>
          </n-upload>
        </div>

        <div class="form-group" v-if="selectedFile">
          <label for="course-name">Course Name (Optional)</label>
          <n-input
            id="course-name"
            v-model:value="courseName"
            placeholder="Enter course name for better analysis"
          />
        </div>

        <div class="upload-actions">
          <n-button @click="cancelUpload" type="default">Cancel</n-button>
          <n-button
            type="primary"
            size="large"
            :loading="uploading"
            :disabled="!selectedFile"
            @click="handleFileUpload"
          >
            {{ uploading ? 'Uploading...' : 'Upload & Analyze' }}
          </n-button>
        </div>
      </form>
    </div>

    <!-- Assignments List -->
    <div class="assignments-list">
      <div v-if="loading" class="loading-state">
        <n-spin size="large" />
        <p>Loading your assignments...</p>
      </div>

      <div v-else-if="assignments.length === 0" class="empty-state">
        <div class="empty-content">
          <n-icon size="64" color="#64748b">
            <FileText />
          </n-icon>
          <h3>No assignments yet</h3>
          <p>Upload your first assignment to get started with AI-powered analysis</p>
          <n-button type="primary" @click="showUpload = true" size="large">
            Upload First Assignment
          </n-button>
        </div>
      </div>

      <div v-else class="assignments-grid">
        <div
          v-for="assignment in assignments"
          :key="assignment.id"
          class="assignment-card card"
          @click="viewAssignment(assignment.id)"
        >
          <div class="assignment-header">
            <h4>{{ assignment.title }}</h4>
            <n-tag
              :type="getStatusType(assignment.status)"
              size="small"
            >
              {{ assignment.status }}
            </n-tag>
          </div>

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
          </div>

          <div v-if="assignment.analysis_available" class="assignment-analysis">
            <span class="analysis-indicator">
              🤖 Analysis complete
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FileImage, FileText, Calendar } from 'lucide-vue-next'
import { api } from '@/services/api'

interface Assignment {
  id: number
  title: string
  original_filename?: string
  corrected_filename?: string
  status: string
  created_at: string
  analysis_available: boolean
}

interface FileInfo {
  id: string
  name: string
  percentage?: number
  status?: string
  url?: string
  file?: File
}

const router = useRouter()
const assignments = ref<Assignment[]>([])
const loading = ref(false)
const showUpload = ref(true)
const fileList = ref<FileInfo[]>([])
const selectedFile = ref<File | null>(null)
const courseName = ref('')
const uploading = ref(false)

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

const handleFileChange = (files: FileInfo[]) => {
  fileList.value = files
  if (files.length > 0 && files[0].file) {
    selectedFile.value = files[0].file
  } else {
    selectedFile.value = null
  }
}

const handleUploadRequest = ({ file }: { file: File }) => {
  // This is handled by our form submission
  return Promise.resolve()
}

const handleFileUpload = async () => {
  if (!selectedFile.value) return

  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    if (courseName.value?.trim?.()) {
      formData.append('course_name', courseName.value?.trim?.() || '')
    }

    const response = await api.post('/assignments/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (window.$message) {
      window.$message.success('Assignment uploaded successfully! Analysis will begin shortly.')
    }

    // Reset form
    fileList.value = []
    selectedFile.value = null
    courseName.value = ''
    showUpload.value = false

    // Reload assignments
    await loadAssignments()

  } catch (error) {
    console.error('Upload failed:', error)
    if (window.$message) {
      window.$message.error('Upload failed. Please try again.')
    }
  } finally {
    uploading.value = false
  }
}

const cancelUpload = () => {
  fileList.value = []
  selectedFile.value = null
  courseName.value = ''
  showUpload.value = false
}

const viewAssignment = (assignmentId: number) => {
  router.push(`/assignments/${assignmentId}`)
}

const loadAssignments = async () => {
  loading.value = true
  try {
    const response = await api.get('/assignments/')
    assignments.value = response.data
  } catch (error) {
    console.error('Failed to load assignments:', error)
    if (window.$message) {
      window.$message.error('Failed to load assignments')
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAssignments()
})
</script>

<style scoped>
.assignments-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.assignments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
}

.upload-btn {
  padding: 0.75rem 1.5rem;
  font-weight: 600;
}

.upload-section {
  margin-bottom: 2rem;
}

.upload-section h2 {
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
  font-weight: 600;
}

.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-md);
  padding: 2rem;
  text-align: center;
  background: rgba(30, 41, 59, 0.3);
  transition: all 0.3s;
  cursor: pointer;
}

.upload-area:hover {
  border-color: var(--primary-color);
  background: rgba(16, 185, 129, 0.1);
}

.upload-text {
  margin: 1rem 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 500;
}

.upload-hint {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.upload-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.assignments-list {
  min-height: 300px;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.empty-content h3 {
  margin: 1rem 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.empty-content p {
  margin: 0 0 2rem 0;
  color: var(--text-secondary);
}

.assignments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.assignment-card {
  cursor: pointer;
  transition: all 0.3s;
}

.assignment-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.assignment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.assignment-header h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  flex: 1;
  margin-right: 1rem;
}

.assignment-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.assignment-analysis {
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-color);
}

.analysis-indicator {
  font-size: 0.9rem;
  color: var(--primary-color);
  font-weight: 500;
}

@media (max-width: 768px) {
  .assignments-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .assignments-grid {
    grid-template-columns: 1fr;
  }

  .assignment-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>