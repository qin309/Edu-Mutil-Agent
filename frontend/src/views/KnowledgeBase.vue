<template>
  <div class="knowledge-base-container">
    <!-- Header -->
    <div class="kb-header">
      <div class="header-content">
        <h1>📚 知识库管理</h1>
        <p>上传和管理文档，建立智能知识库</p>
      </div>
      <div class="header-actions">
        <n-button type="primary" size="large" @click="showUploadModal = true">
          <template #icon>
            <Upload />
          </template>
          上传文档
        </n-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-section" v-if="stats">
      <div class="stats-grid">
        <div class="stat-card" v-for="(count, type) in stats.document_types" :key="type">
          <div class="stat-icon">
            <FileText v-if="type.includes('text')" />
            <File v-else-if="type.includes('pdf')" />
            <File v-else />
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ count }}</div>
            <div class="stat-label">{{ formatDocType(type) }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <Database />
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_documents }}</div>
            <div class="stat-label">总文档数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <BookOpen />
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ formatBytes(stats.total_content_length) }}</div>
            <div class="stat-label">内容总量</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" :class="{ 'inactive': !stats.lightrag_available }">
            <Zap />
          </div>
          <div class="stat-info">
            <div class="stat-value" :class="{ 'inactive': !stats.lightrag_available }">
              {{ stats.lightrag_available ? '在线' : '离线' }}
            </div>
            <div class="stat-label">RAG引擎状态</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Documents List -->
    <div class="documents-section">
      <div class="section-header">
        <h2>文档列表</h2>
        <n-button @click="refreshDocuments" :loading="loading" type="tertiary">
          <template #icon>
            <RefreshCw />
          </template>
          刷新
        </n-button>
      </div>

      <div class="documents-grid" v-if="documents.length > 0">
        <div
          class="document-card"
          v-for="(doc, index) in documents"
          :key="index"
        >
          <div class="doc-header">
            <div class="doc-icon">
              <FileText v-if="doc.type.includes('text')" />
              <File v-else-if="doc.type.includes('pdf')" />
              <File v-else />
            </div>
            <div class="doc-info">
              <h3 class="doc-title">{{ doc.title }}</h3>
              <div class="doc-meta">
                <span class="doc-type">{{ formatDocType(doc.type) }}</span>
                <span class="doc-size">{{ formatBytes(doc.content_length || 0) }}</span>
                <n-tag :type="getStatusType(doc.status)" size="small">
                  {{ doc.status === 'active' ? '活跃' : '禁用' }}
                </n-tag>
              </div>
            </div>
          </div>
          <div class="doc-content">
            <p class="doc-preview">
              {{ doc.filename }}
            </p>
            <div class="doc-actions">
              <n-button size="small" type="primary" text @click="queryDocument(doc)">
                <template #icon>
                  <Search />
                </template>
                查询
              </n-button>
              <n-button size="small" type="error" text @click="deleteDocument(doc)">
                <template #icon>
                  <Trash2 />
                </n-button>
              </n-button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div class="empty-state" v-else-if="!loading">
        <div class="empty-content">
          <n-icon size="64" color="var(--text-muted)">
            <BookOpen />
          </n-icon>
          <h3>知识库为空</h3>
          <p>开始上传文档来构建您的知识库吧！</p>
          <n-button type="primary" @click="showUploadModal = true">
            <template #icon>
              <Upload />
            </template>
            上传第一个文档
          </n-button>
        </div>
      </div>

      <!-- Loading -->
      <div class="loading-state" v-else>
        <n-spin size="large" />
        <p>加载文档列表...</p>
      </div>
    </div>

    <!-- Upload Modal -->
    <n-modal v-model:show="showUploadModal" preset="card" title="上传文档" size="huge">
      <div class="upload-modal">
        <div class="upload-zone" @drop.prevent="handleFileDrop" @dragover.prevent>
          <input
            ref="fileInput"
            type="file"
            multiple
            accept=".txt,.md,.pdf,.docx,.doc"
            @change="handleFileSelect"
            style="display: none"
          />

          <div class="upload-area" v-if="!selectedFiles.length" @click="$refs.fileInput.click()">
            <n-icon size="48" color="var(--text-muted)">
              <Upload />
            </n-icon>
            <h3>点击或拖拽文件到此处</h3>
            <p>支持 .txt, .md, .pdf, .docx, .doc 文件</p>
            <p class="upload-hint">最大文件大小: 10MB</p>
          </div>

          <div class="file-list" v-else>
            <div class="file-item" v-for="(file, index) in selectedFiles" :key="index">
              <div class="file-info">
                <n-icon size="24">
                  <File />
                </n-icon>
                <div class="file-details">
                  <div class="file-name">{{ file.name }}</div>
                  <div class="file-size">{{ formatBytes(file.size) }}</div>
                </div>
              </div>
              <n-button size="small" type="error" @click="removeFile(index)">
                <template #icon>
                  <X />
                </n-button>
              </n-button>
            </div>
            <div class="file-actions">
              <n-button @click="$refs.fileInput.click()">添加更多文件</n-button>
              <n-button @click="clearFiles" type="tertiary">清空</n-button>
            </div>
          </div>
        </div>

        <div class="upload-form">
          <n-form :model="uploadForm" label-placement="top">
            <n-form-item label="文档标题 (可选)">
              <n-input
                v-model:value="uploadForm.title"
                placeholder="请输入文档标题，如果为空将使用文件名"
              />
            </n-form-item>
            <n-form-item label="课程名称 (可选)">
              <n-input
                v-model:value="uploadForm.courseName"
                placeholder="输入课程名称以便更好分析"
              />
            </n-form-item>
            <n-form-item label="知识库名称 (可选)">
              <n-input
                v-model:value="uploadForm.knowledgeBaseName"
                placeholder="指定知识库名称，默认为 general"
              />
            </n-form-item>
          </n-form>
        </div>

        <div class="modal-actions">
          <n-button @click="showUploadModal = false">取消</n-button>
          <n-button
            type="primary"
            @click="uploadDocuments"
            :loading="uploading"
            :disabled="!selectedFiles.length"
          >
            上传 {{ selectedFiles.length }} 个文件
          </n-button>
        </div>
      </div>
    </n-modal>

    <!-- Query Result Modal -->
    <n-modal v-model:show="showQueryModal" preset="card" title="查询结果" size="huge">
      <div class="query-modal">
        <div class="query-content" v-if="queryResult">
          <div class="query-question">
            <h4>问题:</h4>
            <p>{{ queryResult.question }}</p>
          </div>
          <div class="query-answer">
            <h4>答案:</h4>
            <div class="answer-content" v-html="formatAnswer(queryResult.answer)"></div>
          </div>
          <div class="query-sources" v-if="queryResult.sources && queryResult.sources.length > 0">
            <h4>来源:</h4>
            <div class="sources-list">
              <span v-for="source in queryResult.sources" :key="source" class="source-tag">
                {{ source }}
              </span>
            </div>
          </div>
        </div>
        <div class="loading" v-else>
          <n-spin size="large" />
          <p>查询中...</p>
        </div>

        <div class="modal-actions" style="margin-top: 20px;">
          <n-button @click="showQueryModal = false">关闭</n-button>
          <n-button type="primary" @click="showQueryModal = false">新查询</n-button>
        </div>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import {
  Upload,
  FileText,
  File,
  Database,
  BookOpen,
  Zap,
  RefreshCw,
  Search,
  Trash2,
  X
} from 'lucide-vue-next'

import { api } from '@/services/api'

interface Document {
  title: string
  type: string
  content_length: number
  filename: string
  status: string
  timestamp: string
  [key: string]: any
}

interface KBStats {
  lightrag_available: boolean
  total_documents: number
  document_types: Record<string, number>
  total_content_length: number
}

interface QueryResult {
  question: string
  answer: string
  sources: string[]
  mode: string
}

// Reactive state
const message = useMessage()
const documents = ref<Document[]>([])
const stats = ref<KBStats | null>(null)
const loading = ref(false)
const uploading = ref(false)
const showUploadModal = ref(false)
const showQueryModal = ref(false)
const selectedFiles = ref<File[]>([])
const fileInput = ref<HTMLInputElement>()
const currentDoc = ref<Document | null>(null)
const queryResult = ref<QueryResult | null>(null)

const uploadForm = reactive({
  title: '',
  courseName: '',
  knowledgeBaseName: ''
})

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDocType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'text/plain': '文本文件',
    'text/markdown': 'Markdown',
    'application/pdf': 'PDF文档',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word文档',
  }
  return typeMap[type] || '未知类型'
}

const getStatusType = (status: string): string => {
  return status === 'active' ? 'success' : 'warning'
}

const formatAnswer = (answer: string): string => {
  if (!answer) return answer
  return answer
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const refreshDocuments = async () => {
  loading.value = true
  try {
    const response = await api.get('/knowledge/documents')
    documents.value = response.data.documents
    stats.value = response.data.stats
  } catch (error) {
    message.error('获取文档列表失败')
    console.error('Failed to refresh documents:', error)
  } finally {
    loading.value = false
  }
}

const handleFileDrop = (event: DragEvent) => {
  const files = Array.from(event.dataTransfer?.files || [])
  addFiles(files)
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = Array.from(target.files || [])
  addFiles(files)
}

const addFiles = (files: File[]) => {
  const validFiles = files.filter(file => {
    const validTypes = ['.txt', '.md', '.pdf', '.docx', '.doc']
    const isValid = validTypes.some(type => file.name.toLowerCase().endsWith(type))
    const isValidSize = file.size <= 10 * 1024 * 1024 // 10MB

    if (!isValid) {
      message.error(`${file.name}: 不支持的文件类型`)
      return false
    }

    if (!isValidSize) {
      message.error(`${file.name}: 文件大小超过10MB限制`)
      return false
    }

    return true
  })

  selectedFiles.value.push(...validFiles)
}

const removeFile = (index: number) => {
  selectedFiles.value.splice(index, 1)
}

const clearFiles = () => {
  selectedFiles.value = []
}

const uploadDocuments = async () => {
  if (!selectedFiles.value.length) return

  uploading.value = true
  let successCount = 0
  let errorCount = 0

  for (const file of selectedFiles.value) {
    try {
      const formData = new FormData()
      formData.append('file', file)
      if (uploadForm.title?.trim?.() && uploadForm.title.trim()) {
        formData.append('title', uploadForm.title.trim())
      }
      if (uploadForm.courseName?.trim?.() && uploadForm.courseName.trim()) {
        formData.append('course_name', uploadForm.courseName.trim())
      }
      if (uploadForm.knowledgeBaseName?.trim?.() && uploadForm.knowledgeBaseName.trim()) {
        formData.append('knowledge_base_name', uploadForm.knowledgeBaseName.trim())
      }

      const response = await api.post('/knowledge/upload-document', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      if (response.data.success) {
        successCount++
        message.success(`${file.name}: ${response.data.message}`)
      } else {
        errorCount++
        message.error(`${file.name}: ${response.data.error || '上传失败'}`)
      }
    } catch (error: any) {
      errorCount++
      const errorMessage = error.response?.data?.detail || error.message || '上传失败'
      message.error(`${file.name}: ${errorMessage}`)
      console.error('Upload error:', error)
    }
  }

  uploading.value = false

  if (successCount > 0) {
    message.success(`成功上传 ${successCount} 个文件`)
    showUploadModal.value = false
    clearFiles()
    uploadForm.title = ''
    uploadForm.courseName = ''
    uploadForm.knowledgeBaseName = ''
    await refreshDocuments()
  }

  if (errorCount > 0) {
    message.warning(`${errorCount} 个文件上传失败`)
  }
}

const queryDocument = async (doc: Document) => {
  const question = `请基于文档"${doc.title}"的内容回答相关问题`

  try {
    const response = await api.post('/knowledge/query', {
      question: question,
      mode: 'hybrid'
    })

    queryResult.value = response.data
    showQueryModal.value = true

  } catch (error) {
    message.error('查询失败')
    console.error('Query error:', error)
  }
}

const deleteDocument = async (doc: Document) => {
  try {
    const response = await api.delete(`/knowledge/documents/${encodeURIComponent(doc.title)}`)

    if (response.data.success) {
      message.success(`文档删除成功: ${doc.title}`)
      await refreshDocuments()
    } else {
      message.error(`文档删除失败: ${doc.title}`)
    }

  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || '删除失败'
    message.error(`文档删除失败: ${errorMessage}`)
    console.error('Delete error:', error)
  }
}

onMounted(() => {
  refreshDocuments()
})
</script>

<style scoped>
.knowledge-base-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.kb-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  gap: 2rem;
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

.stats-section {
  margin-bottom: 3rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.2s;
}

.stat-card:hover {
  border-color: var(--primary-color);
  box-shadow: var(--box-shadow);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: rgba(16, 185, 129, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
}

.stat-icon.inactive {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.stat-value.inactive {
  color: #ef4444;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.documents-section {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 2rem;
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

.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.document-card {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  transition: all 0.2s;
}

.document-card:hover {
  border-color: var(--primary-color);
  box-shadow: var(--box-shadow);
}

.doc-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.doc-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: rgba(16, 185, 129, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
}

.doc-info {
  flex: 1;
}

.doc-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.doc-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.doc-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.doc-preview {
  flex: 1;
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.doc-actions {
  display: flex;
  gap: 0.5rem;
}

.upload-modal {
  min-height: 400px;
}

.upload-zone {
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-md);
  padding: 2rem;
  text-align: center;
  margin-bottom: 2rem;
  transition: all 0.2s;
}

.upload-zone:hover {
  border-color: var(--primary-color);
  background: rgba(16, 185, 129, 0.05);
}

.upload-area {
  cursor: pointer;
  padding: 2rem 0;
}

.upload-area h3 {
  margin: 1rem 0 0.5rem 0;
  color: var(--text-primary);
}

.upload-area p {
  color: var(--text-secondary);
  margin: 0.25rem 0;
}

.upload-hint {
  font-size: 0.85rem !important;
}

.file-list {
  max-height: 300px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  margin-bottom: 0.5rem;
}

.file-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.file-size {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.file-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.upload-form {
  margin-bottom: 2rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.query-modal {
  min-height: 300px;
}

.query-content {
  margin-bottom: 2rem;
}

.query-question,
.query-answer,
.query-sources {
  margin-bottom: 1.5rem;
}

.query-question h4,
.query-answer h4,
.query-sources h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.answer-content {
  line-height: 1.6;
  color: var(--text-secondary);
}

.sources-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.source-tag {
  background: rgba(16, 185, 129, 0.1);
  color: var(--primary-color);
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
}

.empty-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-content h3 {
  margin: 1rem 0 0.5rem 0;
  color: var(--text-primary);
}

.empty-content p {
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.loading-state {
  padding: 3rem;
}

@media (max-width: 768px) {
  .kb-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    margin-top: 1rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .documents-grid {
    grid-template-columns: 1fr;
  }

  .doc-content {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .doc-actions {
    justify-content: center;
  }

  .section-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
}
</style>