<template>
  <div class="knowledge-page">
    <!-- Knowledge Base Interface -->
    <div class="knowledge-header">
      <div class="header-main">
        <div class="title-section">
          <h2 class="page-title">📚 Knowledge Base</h2>
          <p class="page-description">Manage and query your knowledge documents</p>
        </div>

        <!-- Knowledge Space Selector -->
        <div class="space-selector">
          <div class="space-controls">
            <n-select
              v-model:value="currentSpace"
              :options="spaceOptions"
              placeholder="Select knowledge space"
              @update:value="switchKnowledgeSpace"
              style="min-width: 200px;"
            />
            <n-button type="primary" @click="showCreateSpaceModal = true" :loading="isCreatingSpace">
              <template #icon>
                <Plus />
              </template>
              New Space
            </n-button>
          </div>
          <div class="current-space-info" v-if="currentSpaceInfo">
            <span class="space-stats">
              {{ currentSpaceInfo.total_documents }} docs
            </span>
            <span class="space-status" :class="currentSpaceInfo.lightrag_available ? 'available' : 'unavailable'">
              {{ currentSpaceInfo.lightrag_available ? 'RAG Available' : 'RAG Offline' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="knowledge-content">
      <!-- Tab Management -->
      <div class="tab-selector">
        <n-radio-group v-model:value="activeTab" size="large">
          <n-radio-button value="search">
            🔍 Search
          </n-radio-button>
          <n-radio-button value="documents">
            📄 Documents
          </n-radio-button>
        </n-radio-group>
      </div>

      <!-- Search Tab Content -->
      <div v-if="activeTab === 'search'" class="tab-content">
        <div class="search-section">
          <h3>Search Knowledge Base</h3>

          <!-- Search Configuration -->
          <div class="search-config">
            <n-form-item label="Search Mode" style="flex: 1;">
              <n-select
                v-model:value="searchMode"
                :options="searchModeOptions"
                placeholder="Select search mode"
              />
            </n-form-item>
            <n-form-item label="AI Model (Optional)" style="flex: 1;">
              <n-input
                v-model:value="searchModel"
                placeholder="Pro/provider/model-name (e.g., Pro/deepseek-ai/DeepSeek-V3.1-Terminus)"
                clearable
              />
            </n-form-item>
          </div>

          <div class="search-input-group">
            <n-input
              v-model:value="searchQuery"
              type="textarea"
              placeholder="Enter your question or search query..."
              :autosize="{ minRows: 3, maxRows: 6 }"
              clearable
            />
            <n-button
              type="primary"
              size="large"
              @click="performSearch"
              :loading="isSearching"
              :disabled="!searchQuery?.trim?.()"
            >
              <template #icon>
                <Search />
              </template>
              Search
            </n-button>
          </div>
        </div>
      </div>

      <!-- Documents Tab Content -->
      <div v-if="activeTab === 'documents'" class="tab-content">
        <div class="documents-section">
          <div class="documents-header">
            <h3>Your Documents</h3>
            <n-button type="primary" @click="showUploadModal = true">
              <template #icon>
                <Upload />
              </template>
              Upload Document
            </n-button>
          </div>

          <div v-if="documents.length > 0" class="documents-list">
            <div
              v-for="(doc, index) in documents"
              :key="index"
              class="document-card"
            >
              <div class="doc-info">
                <h4>{{ doc.title || doc.filename }}</h4>
                <p>{{ doc.filename }}</p>
                <n-tag :type="doc.status === 'active' ? 'success' : 'warning'">
                  {{ doc.status === 'active' ? 'Active' : 'Inactive' }}
                </n-tag>
              </div>
              <div class="doc-actions">
                <n-button size="small" @click="queryDocument(doc)">
                  Query
                </n-button>
                <n-button size="small" type="error" @click="deleteDocument(doc)">
                  Delete
                </n-button>
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <n-empty description="No documents uploaded yet">
              <template #extra>
                <n-button type="primary" @click="showUploadModal = true">
                  Upload Your First Document
                </n-button>
              </template>
            </n-empty>
          </div>
        </div>
      </div>
    </div>

    <!-- Search Results Modal -->
    <n-modal v-model:show="showResultsModal" preset="card" title="Search Results" size="huge">
      <div class="results-modal">
        <div v-if="searchResults">
          <div class="search-question">
            <h4>Question:</h4>
            <p>{{ searchResults.question }}</p>
          </div>
          <div class="search-answer">
            <h4>Answer:</h4>
            <div v-html="searchResults.answer"></div>
          </div>
          <div v-if="searchResults.sources?.length > 0" class="search-sources">
            <h4>Sources:</h4>
            <div class="sources-list">
              <n-tag v-for="source in searchResults.sources" :key="source" size="small">
                {{ source }}
              </n-tag>
            </div>
          </div>
        </div>
        <div v-else class="loading-state">
          <n-spin size="large" />
          <p>{{ isSearching ? 'Searching...' : 'No results found' }}</p>
        </div>
      </div>
    </n-modal>

    <!-- Upload Modal -->
    <n-modal v-model:show="showUploadModal" preset="card" title="Upload Documents" size="huge">
      <div class="upload-modal">
        <n-form :model="uploadForm" label-placement="top">
          <n-form-item label="Select Files">
            <div class="file-upload-zone">
              <input
                ref="fileInputRef"
                type="file"
                multiple
                accept=".txt,.md,.pdf,.docx,.doc"
                @change="handleFileSelect"
                style="display: none"
              />
              <n-button
                type="primary"
                @click="$refs.fileInputRef?.click()"
                :disabled="selectedFiles.length >= 5"
              >
                <template #icon>
                  <Upload />
                </template>
                Select Files
              </n-button>

              <!-- File list -->
              <div v-if="selectedFiles.length > 0" class="selected-files">
                <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
                  <span class="file-name">{{ file.name }}</span>
                  <span class="file-size">({{ formatFileSize(file.size) }})</span>
                  <n-button size="small" type="error" @click="removeFile(index)">×</n-button>
                </div>
                <n-button @click="clearFiles" type="tertiary" size="small">Clear All</n-button>
              </div>
            </div>

            <n-text style="margin-top: 8px; font-size: 12px; color: var(--text-secondary);">
              Maximum 5 files, 10MB each. Supported: .txt, .md, .pdf, .docx, .doc
            </n-text>
          </n-form-item>

          <n-form-item label="Document Title (Optional)">
            <n-input
              v-model:value="uploadForm.title"
              placeholder="Auto-generated from file name if empty"
              clearable
            />
          </n-form-item>

          <n-form-item label="Course Name (Optional)">
            <n-input
              v-model:value="uploadForm.courseName"
              placeholder="Help categorize the document"
              clearable
            />
          </n-form-item>

          <n-form-item label="AI Model for Indexing (Optional)">
            <n-input
              v-model:value="uploadForm.model"
              placeholder="Pro/provider/model-name (e.g., Pro/deepseek-ai/DeepSeek-V3.1-Terminus)"
              clearable
            />
            <n-text style="margin-top: 8px; font-size: 12px; color: var(--text-secondary);">
              Specify a custom AI model for document indexing. Leave empty to use default model.
            </n-text>
          </n-form-item>
        </n-form>

        <!-- Upload Progress -->
        <div v-if="isUploading && uploadProgress.length > 0" class="upload-progress-section">
          <n-divider style="margin: 1rem 0;" />
          <h4 style="margin-bottom: 1rem;">Upload Progress</h4>
          <div class="progress-list">
            <div v-for="(progress, index) in uploadProgress" :key="index" class="progress-item">
              <div class="progress-header">
                <span class="progress-filename">{{ progress.filename }}</span>
                <span class="progress-status" :class="progress.status">
                  {{ progress.status === 'uploading' ? 'Uploading...' : progress.status === 'success' ? '✓ Success' : '✗ Failed' }}
                </span>
              </div>
              <n-progress
                v-if="progress.status === 'uploading'"
                type="line"
                :percentage="progress.percentage"
                :status="progress.status === 'success' ? 'success' : progress.status === 'error' ? 'error' : 'default'"
                :show-indicator="false"
              />
              <div v-if="progress.message" class="progress-message" :class="progress.status">
                {{ progress.message }}
              </div>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <n-button @click="resetUploadForm">Cancel</n-button>
          <n-button
            type="primary"
            @click="uploadDocuments"
            :loading="isUploading"
            :disabled="!selectedFiles.length"
          >
            Upload {{ selectedFiles.length }} file{{ selectedFiles.length !== 1 ? 's' : '' }}
          </n-button>
        </div>
      </div>
    </n-modal>

    <!-- Create Knowledge Space Modal -->
    <n-modal v-model:show="showCreateSpaceModal" preset="card" title="Create New Knowledge Space" size="small">
      <div class="create-space-modal">
        <n-form :model="{ name: spaceNameInput }" label-placement="top">
          <n-form-item label="Space Name" :feedback="spaceNameInput?.length > 50 ? 'Name too long (max 50 chars)' : ''" :validationStatus="spaceNameInput?.length > 50 ? 'error' : 'success'">
            <n-input
              v-model:value="spaceNameInput"
              placeholder="Enter knowledge space name"
              clearable
              maxlength="50"
              show-count
              @keydown.enter="createKnowledgeSpace"
            />
          </n-form-item>

          <div class="modal-help">
            <p>Knowledge spaces allow you to organize documents into separate knowledge bases.</p>
            <ul>
              <li>Each space has its own LightRAG instance for AI reasoning</li>
              <li>Spaces help organize course materials and assignments</li>
              <li>You can switch between spaces anytime</li>
            </ul>
          </div>
        </n-form>

        <div class="modal-actions">
          <n-button @click="showCreateSpaceModal = false">Cancel</n-button>
          <n-button
            type="primary"
            @click="createKnowledgeSpace"
            :loading="isCreatingSpace"
            :disabled="!spaceNameInput?.trim?.() || spaceNameInput?.length > 50"
          >
            Create Space
          </n-button>
        </div>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Search, Upload, Plus } from 'lucide-vue-next'
import { useMessage } from 'naive-ui'
import { api } from '@/services/api'

// Tab management
const activeTab = ref('search')
const searchQuery = ref('')
const isSearching = ref(false)
const showResultsModal = ref(false)
const showUploadModal = ref(false)
const isUploading = ref(false)
const documents = ref([])
const searchResults = ref(null)

// Search configuration
const searchMode = ref('hybrid')
const searchModel = ref<string | null>(null)

const searchModeOptions = [
  { label: 'Hybrid (Recommended)', value: 'hybrid' },
  { label: 'Local Search', value: 'local' },
  { label: 'Global Search', value: 'global' },
  { label: 'Naive Search', value: 'naive' }
]

// Knowledge spaces
const knowledgeSpaces = ref([] as any[])
const currentSpace = ref('default')
const showCreateSpaceModal = ref(false)
const spaceNameInput = ref('')
const isCreatingSpace = ref(false)

// Upload form
const selectedFiles = ref<File[]>([])
const uploadForm = ref({
  title: '',
  courseName: '',
  model: ''
})
const fileInputRef = ref<HTMLInputElement>()

// Upload progress tracking
const uploadProgress = ref<Array<{
  filename: string
  percentage: number
  status: 'uploading' | 'success' | 'error'
  message?: string
}>>([])

const message = useMessage()

onMounted(() => {
  console.log('Knowledge component mounted successfully!')
  loadKnowledgeSpaces()
  loadDocuments()
})

const performSearch = async () => {
  if (!searchQuery.value?.trim?.()) return

  isSearching.value = true
  const startTime = Date.now()
  
  // Show progress message
  let progressInterval: NodeJS.Timeout | null = null
  
  try {
    // Start progress indicator for long queries
    progressInterval = setInterval(() => {
      const elapsed = (Date.now() - startTime) / 1000
      if (elapsed > 10) {
        message.info(`Processing your query... ${Math.round(elapsed)}s elapsed`, {
          duration: 2000
        })
      }
    }, 10000) // Update every 10 seconds
    
    const requestData: any = {
      question: searchQuery.value,
      mode: searchMode.value
    }

    // Add model parameter if a specific model is selected
    if (searchModel.value) {
      requestData.model = searchModel.value
    }

    const response = await api.post('/knowledge/query', requestData, {
      params: {
        space_name: currentSpace.value
      },
      timeout: 120000 // 120 seconds - increased to match backend 90s timeout + buffer
    })

    searchResults.value = response.data
    showResultsModal.value = true
    
    const totalTime = (Date.now() - startTime) / 1000
    console.log(`Query completed in ${totalTime.toFixed(2)} seconds`)
    
  } catch (error) {
    const totalTime = (Date.now() - startTime) / 1000
    console.log(`Query failed after ${totalTime.toFixed(2)} seconds`)
    
    if (error.code === 'ECONNABORTED') {
      message.error('Query timed out. The system may be processing a complex request. Please try a simpler query or try again later.')
    } else {
      message.error('Search failed. Please try again.')
    }
    console.error('Search error:', error)
  } finally {
    if (progressInterval) {
      clearInterval(progressInterval)
    }
    isSearching.value = false
  }
}

const loadDocuments = async () => {
  try {
    const response = await api.get('/knowledge/documents', {
      params: {
        space_name: currentSpace.value
      }
    })
    documents.value = response.data.documents || []
  } catch (error) {
    console.error('Failed to load documents:', error)
  }
}

const queryDocument = async (doc: any) => {
  searchQuery.value = `Please analyze the document "${doc.title || doc.filename}"`
  activeTab.value = 'search'
  await performSearch()
}

const deleteDocument = async (doc: any) => {
  try {
    await api.delete(`/knowledge/documents/${encodeURIComponent(doc.title || doc.filename)}`, {
      params: {
        space_name: currentSpace.value
      }
    })
    message.success('Document deleted successfully')
    loadDocuments()
  } catch (error) {
    message.error('Failed to delete document')
    console.error('Delete error:', error)
  }
}

// Upload handling functions
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    const files = Array.from(target.files)

    // Validate files
    const validFiles = files.filter(file => {
      const validTypes = ['.txt', '.md', '.pdf', '.docx', '.doc']
      const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
      const isValidType = validTypes.includes(fileExt)
      const isValidSize = file.size <= 10 * 1024 * 1024 // 10MB

      if (!isValidType) {
        message.error(`${file.name}: Unsupported file type`)
        return false
      }

      if (!isValidSize) {
        message.error(`${file.name}: File size exceeds 10MB limit`)
        return false
      }

      return true
    })

    // Check total file count
    if (selectedFiles.value.length + validFiles.length > 5) {
      message.error('Maximum 5 files allowed')
      return
    }

    selectedFiles.value.push(...validFiles)
    console.log('Files selected:', selectedFiles.value)
  }
}

const removeFile = (index: number) => {
  selectedFiles.value.splice(index, 1)
}

const clearFiles = () => {
  selectedFiles.value = []
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// Computed properties for knowledge spaces
const spaceOptions = computed(() => {
  return knowledgeSpaces.value.map((space: any) => ({
    label: `${space.space_name} (${space.total_documents} docs)`,
    value: space.space_name
  }))
})

const currentSpaceInfo = computed(() => {
  return knowledgeSpaces.value.find((space: any) => space.space_name === currentSpace.value)
})

const resetUploadForm = () => {
  showUploadModal.value = false
  selectedFiles.value = []
  uploadForm.value = {
    title: '',
    courseName: '',
    model: ''
  }
}

const uploadDocuments = async () => {
  if (!selectedFiles.value.length) return

  isUploading.value = true
  let successCount = 0
  let errorCount = 0

  const totalFiles = selectedFiles.value.length
  console.log(`Starting upload of ${totalFiles} files`)

  // Initialize progress tracking
  uploadProgress.value = selectedFiles.value.map(file => ({
    filename: file.name,
    percentage: 0,
    status: 'uploading' as const,
    message: 'Preparing upload...'
  }))

  // Upload files one by one
  for (let i = 0; i < selectedFiles.value.length; i++) {
    const file = selectedFiles.value[i]

    try {
      console.log(`Uploading file ${i + 1}/${totalFiles}: ${file.name}`)

      // Update progress: uploading
      uploadProgress.value[i].percentage = 10
      uploadProgress.value[i].message = 'Uploading file...'

      // Create FormData for upload
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', uploadForm.value.title || '')
      formData.append('course_name', uploadForm.value.courseName || '')
      formData.append('space_name', currentSpace.value || 'default')  // Use currentSpace instead of knowledgeBaseName

      // Add model parameter if specified
      if (uploadForm.value.model?.trim?.()) {
        formData.append('model', uploadForm.value.model)
      }

      console.log('FormData prepared, sending API request...')

      // Update progress: processing
      uploadProgress.value[i].percentage = 30
      uploadProgress.value[i].message = 'Processing document...'

      const response = await api.post('/knowledge/upload-document', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 180000, // Increased to 180 seconds (3 minutes) for large document indexing
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 50) / progressEvent.total) + 30
            uploadProgress.value[i].percentage = Math.min(percentCompleted, 80)
            uploadProgress.value[i].message = 'Indexing with LightRAG...'
          }
        }
      })

      // Update progress: completed
      uploadProgress.value[i].percentage = 100
      uploadProgress.value[i].status = 'success'
      uploadProgress.value[i].message = 'Successfully indexed!'

      if (response.data && response.data.success) {
        successCount++
        message.success(`${file.name}: Upload successful`)
        console.log(`${file.name}: Upload successful`, response.data)
      } else {
        errorCount++
        uploadProgress.value[i].status = 'error'
        const errorMsg = response.data?.error || 'Upload failed'
        uploadProgress.value[i].message = errorMsg
        message.error(`${file.name}: ${errorMsg}`)
        console.error(`${file.name} upload failed:`, response.data)
      }

    } catch (error: any) {
      errorCount++
      uploadProgress.value[i].percentage = 100
      uploadProgress.value[i].status = 'error'
      const errorMsg = error.response?.data?.detail ||
                      error.message ||
                      'Network error'
      uploadProgress.value[i].message = errorMsg
      message.error(`${file.name}: ${errorMsg}`)
      console.error(`${file.name} upload error:`, error)
    }
  }

  // Update loading state
  isUploading.value = false

  // Show completion summary
  if (successCount > 0) {
    message.success(`Successfully uploaded ${successCount} file${successCount !== 1 ? 's' : ''}`)
    // Don't reset immediately, let user see the progress
    setTimeout(() => {
      resetUploadForm()
      uploadProgress.value = []
    }, 3000)
    await loadDocuments() // Refresh document list
  }

  if (errorCount > 0) {
    message.warning(`${errorCount} file${errorCount !== 1 ? 's' : ''} failed to upload`)
  }

  console.log(`Upload complete. Success: ${successCount}, Errors: ${errorCount}`)
}

// Knowledge space management functions
const loadKnowledgeSpaces = async () => {
  try {
    const response = await api.get('/knowledge/spaces')
    knowledgeSpaces.value = response.data || []

    // Check if current space still exists, otherwise default to 'default'
    const spaceExists = knowledgeSpaces.value.some((space: any) => space.space_name === currentSpace.value)
    if (!spaceExists) {
      currentSpace.value = 'default'
    }
  } catch (error) {
    console.error('Failed to load knowledge spaces:', error)
    message.error('Failed to load knowledge spaces')
  }
}

const createKnowledgeSpace = async () => {
  if (!spaceNameInput.value?.trim?.()) return

  isCreatingSpace.value = true
  try {
    const response = await api.post('/knowledge/spaces', {
      space_name: spaceNameInput.value.trim()
    })

    if (response.data.success) {
      message.success(`Knowledge space "${response.data.space_name}" created successfully`)
      showCreateSpaceModal.value = false
      spaceNameInput.value = ''
      currentSpace.value = response.data.space_name
      await loadKnowledgeSpaces()
    }
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to create knowledge space'
    message.error(errorMessage)
  } finally {
    isCreatingSpace.value = false
  }
}

const switchKnowledgeSpace = async (spaceName: string) => {
  currentSpace.value = spaceName
  await loadDocuments()

  const space = knowledgeSpaces.value.find((s: any) => s.space_name === spaceName)
  if (space) {
    message.info(`Switched to knowledge space: ${spaceName}`)
  }
}
</script>

<style scoped>
.knowledge-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.knowledge-header {
  margin-bottom: 2rem;
  text-align: center;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.page-description {
  font-size: 1.1rem;
  color: var(--text-secondary);
  margin: 0;
}

.knowledge-content {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-md);
}

.tab-selector {
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1rem;
}

.tab-content {
  min-height: 400px;
}

/* Search Section */
.search-section h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.search-config {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.search-config .n-form-item {
  margin-bottom: 0;
}

.search-input-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Documents Section */
.documents-section h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.documents-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.documents-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.document-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: all 0.2s;
}

.document-card:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-sm);
}

.doc-info h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.doc-info p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.doc-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: auto;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  color: var(--text-secondary);
}

/* Modal Styles */
.results-modal,
.upload-modal,
.create-space-modal {
  padding: 1rem 0;
}

.search-question,
.search-answer,
.search-sources {
  margin-bottom: 1.5rem;
}

.search-question h4,
.search-answer h4,
.search-sources h4 {
  margin: 0 0 0.75rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.search-answer div {
  line-height: 1.6;
  color: var(--text-secondary);
}

.sources-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  color: var(--text-secondary);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.modal-help {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(16, 185, 129, 0.05);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: var(--radius-md);
  font-size: 0.9rem;
}

.modal-help p {
  margin: 0 0 0.75rem 0;
  color: var(--text-secondary);
}

.modal-help ul {
  margin: 0 0 0 1rem;
  color: var(--text-secondary);
}

.modal-help li {
  margin-bottom: 0.25rem;
}

.file-upload-zone {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.selected-files {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: rgba(30, 41, 59, 0.3);
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  background: var(--bg-primary);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
}

.file-name {
  flex: 1;
  font-weight: 500;
  color: var(--text-primary);
}

.file-size {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

/* Upload Progress Styles */
.upload-progress-section {
  margin-top: 1.5rem;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.progress-item {
  padding: 1rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.progress-filename {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.progress-status {
  font-size: 0.85rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
}

.progress-status.uploading {
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
}

.progress-status.success {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.progress-status.error {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.progress-message {
  font-size: 0.8rem;
  margin-top: 0.5rem;
  padding: 0.5rem;
  border-radius: var(--radius-sm);
  background: var(--bg-secondary);
}

.progress-message.uploading {
  color: var(--text-secondary);
}

.progress-message.success {
  color: #10b981;
  background: rgba(16, 185, 129, 0.05);
}

.progress-message.error {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
}

/* Responsive Design */
@media (max-width: 768px) {
  .knowledge-page {
    padding: 1rem;
  }

  .knowledge-content {
    padding: 1rem;
  }

  .documents-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .documents-list {
    grid-template-columns: 1fr;
  }

  .doc-actions {
    justify-content: stretch;
  }
}
</style>