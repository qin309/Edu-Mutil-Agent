<template>
  <div class="chat-container">
    <!-- Chat Header -->
    <div class="chat-header">
      <div class="header-info">
        <h1>AI Learning Assistant</h1>
        <p>Ask questions, get explanations, and explore your course materials</p>
      </div>
      <div class="chat-controls">
        <n-input
          v-model:value="selectedModel"
          placeholder="Pro/provider/model-name (e.g., Pro/deepseek-ai/DeepSeek-V3.1-Terminus)"
          style="width: 420px; margin-right: 0.5rem;"
          size="small"
          clearable
        />
        <n-button @click="clearChat" type="tertiary" size="small">
          Clear Chat
        </n-button>
        <n-button @click="exportChat" type="primary" size="small">
          Export Chat
        </n-button>
      </div>
    </div>

    <!-- Chat Messages Area -->
    <div class="chat-messages" ref="messagesContainer">
      <!-- Welcome Message -->
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="welcome-content">
          <div class="ai-avatar">🤖</div>
          <div class="welcome-text">
            <h3>Welcome to your AI Learning Assistant!</h3>
            <p>I can help you with:</p>
            <ul>
              <li>Explaining difficult concepts from your assignments</li>
              <li>Providing study recommendations</li>
              <li>Analyzing your learning progress</li>
              <li>Answering questions about course materials</li>
            </ul>
            <p>Just type your question below to get started!</p>
          </div>
        </div>

        <!-- Quick Start Buttons -->
        <div class="quick-start">
          <h4>Quick Start:</h4>
          <div class="quick-buttons">
            <n-button
              v-for="quick in quickStarters"
              :key="quick"
              type="tertiary"
              size="small"
              @click="sendQuickMessage(quick)"
            >
              {{ quick }}
            </n-button>
          </div>
        </div>
      </div>

      <!-- Chat Messages -->
      <div v-for="(message, index) in messages" :key="index" class="message" :class="message.type">
        <div class="message-avatar">
          <div v-if="message.type === 'user'" class="user-avatar">{{ userInitial }}</div>
          <div v-else class="ai-avatar">🤖</div>
        </div>
        <div class="message-content">
          <div class="message-text" v-html="formatMessage(message.content)"></div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          <div v-if="message.sources && message.sources.length > 0" class="message-sources">
            <h5>Sources:</h5>
            <div class="sources-list">
              <span v-for="source in message.sources" :key="source" class="source-tag">
                {{ source }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Typing Indicator -->
      <div v-if="isTyping" class="message ai typing">
        <div class="message-avatar">
          <div class="ai-avatar">🤖</div>
        </div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Chat Input -->
    <div class="chat-input">
      <div class="input-container">
        <n-input
          v-model:value="currentMessage"
          type="textarea"
          placeholder="Ask me anything about your studies..."
          :autosize="{ minRows: 1, maxRows: 4 }"
          @keydown.enter.exact.prevent="sendMessage"
          @keydown.enter.shift.exact="addNewLine"
          :disabled="isTyping"
        />
        <div class="input-actions">
          <n-button
            type="primary"
            @click="sendMessage"
            :disabled="!currentMessage?.trim?.() || isTyping"
            :loading="isTyping"
          >
            <template #icon>
              <Send />
            </template>
            Send
          </n-button>
        </div>
      </div>
      <div class="input-hint">
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Send } from 'lucide-vue-next'
import { api } from '@/services/api'

interface ChatMessage {
  type: 'user' | 'ai'
  content: string
  timestamp: number
  sources?: string[]
}

const authStore = useAuthStore()
const messages = ref<ChatMessage[]>([])
const currentMessage = ref('')
const isTyping = ref(false)
const messagesContainer = ref<HTMLElement>()

// Model selection (manual text input)
const selectedModel = ref<string>('')

const userInitial = computed(() => {
  const user = authStore.user
  if (user?.full_name && typeof user.full_name === 'string' && user.full_name.length > 0) {
    return user.full_name.charAt(0).toUpperCase()
  }
  if (user?.email && typeof user.email === 'string' && user.email.length > 0) {
    return user.email.charAt(0).toUpperCase()
  }
  return 'U'
})

const quickStarters = [
  "Explain my latest assignment analysis",
  "What areas should I focus on improving?",
  "Show me my learning progress",
  "Help me understand a difficult concept"
]

// Load chat history from localStorage
const loadChatHistory = () => {
  try {
    const history = localStorage.getItem('eduagent_chat_history')
    if (history) {
      messages.value = JSON.parse(history)
    }
  } catch (error) {
    console.error('Failed to load chat history:', error)
  }
}

// Save chat history to localStorage
const saveChatHistory = () => {
  try {
    localStorage.setItem('eduagent_chat_history', JSON.stringify(messages.value))
  } catch (error) {
    console.error('Failed to save chat history:', error)
  }
}

const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  })
}

const formatMessage = (content: string) => {
  // Simple markdown-like formatting
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const addNewLine = () => {
  currentMessage.value += '\n'
}

const sendQuickMessage = (message: string) => {
  currentMessage.value = message
  sendMessage()
}

const sendMessage = async () => {
  if (!currentMessage.value?.trim?.() || isTyping.value) return

  const userMessage: ChatMessage = {
    type: 'user',
    content: currentMessage.value?.trim?.() || '',
    timestamp: Date.now()
  }

  messages.value.push(userMessage)
  const messageToSend = currentMessage.value?.trim?.() || ''
  currentMessage.value = ''
  isTyping.value = true

  scrollToBottom()
  saveChatHistory()

  try {
    // Call the chat API with selected model
    const requestData: any = {
      message: messageToSend,
      student_id: authStore.user?.id?.toString() || 'unknown'
    }

    // Add model parameter if a specific model is selected
    if (selectedModel.value) {
      requestData.model = selectedModel.value
    }

    const response = await api.post('/chat/message', requestData)

    const aiMessage: ChatMessage = {
      type: 'ai',
      content: response.data.response || response.data.message || 'I received your message but had trouble generating a response.',
      timestamp: Date.now(),
      sources: response.data.sources || []
    }

    messages.value.push(aiMessage)

  } catch (error) {
    console.error('Chat API error:', error)

    // Fallback response
    const aiMessage: ChatMessage = {
      type: 'ai',
      content: `I understand you're asking: "${messageToSend}"\n\nI'm having trouble connecting to the knowledge base right now, but I can still help! Based on typical educational patterns:\n\n**For study questions:** Focus on understanding the core concepts rather than memorizing steps.\n\n**For assignment help:** Break down complex problems into smaller, manageable parts.\n\n**For progress tracking:** Regular practice and reviewing mistakes are key to improvement.\n\nCould you provide more specific details about what you'd like help with?`,
      timestamp: Date.now(),
      sources: ['General Study Guidelines']
    }

    messages.value.push(aiMessage)
  } finally {
    isTyping.value = false
    scrollToBottom()
    saveChatHistory()
  }
}

const clearChat = () => {
  messages.value = []
  saveChatHistory()
}

const exportChat = () => {
  const chatText = messages.value.map(msg => {
    const sender = msg.type === 'user' ? 'You' : 'AI Assistant'
    const time = formatTime(msg.timestamp)
    return `[${time}] ${sender}: ${msg.content}`
  }).join('\n\n')

  const blob = new Blob([chatText], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `eduagent-chat-${new Date().toISOString().split('T')[0]}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

onMounted(() => {
  loadChatHistory()
  scrollToBottom()
})
</script>

<style scoped>
.chat-container {
  display: grid;
  grid-template-rows: auto 1fr auto;
  height: calc(100vh - 100px);
  max-width: 1200px;
  margin: 0 auto;
  background: var(--bg-secondary);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(59, 130, 246, 0.1));
  border-bottom: 1px solid var(--border-color);
}

.header-info h1 {
  margin: 0 0 0.25rem 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.header-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.chat-controls {
  display: flex;
  gap: 0.75rem;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.welcome-message {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 700px;
  margin: 2rem auto;
  text-align: center;
}

.welcome-content {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
  text-align: left;
  padding: 2rem;
  background: rgba(16, 185, 129, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.welcome-text h3 {
  margin: 0 0 1rem 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
}

.welcome-text p {
  margin: 0 0 1rem 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.welcome-text ul {
  margin: 0 0 1rem 1.5rem;
  color: var(--text-secondary);
}

.welcome-text li {
  margin-bottom: 0.5rem;
}

.quick-start h4 {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.quick-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
}

.message {
  display: flex;
  gap: 1rem;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.ai {
  align-self: flex-start;
}

.message-avatar {
  flex-shrink: 0;
}

.user-avatar, .ai-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.1rem;
}

.user-avatar {
  background: linear-gradient(135deg, #3B82F6, #1D4ED8);
  color: white;
}

.ai-avatar {
  background: linear-gradient(135deg, #10B981, #059669);
  color: white;
  font-size: 1.2rem;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message.user .message-content {
  text-align: right;
}

.message-text {
  background: var(--bg-primary);
  padding: 1rem 1.25rem;
  border-radius: 16px;
  line-height: 1.5;
  word-wrap: break-word;
  border: 1px solid var(--border-color);
}

.message.user .message-text {
  background: linear-gradient(135deg, #3B82F6, #2563EB);
  color: white;
  border-color: #3B82F6;
}

.message.ai .message-text {
  background: var(--bg-secondary);
  border-color: var(--border-color);
}

.message-time {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.5rem;
}

.message-sources {
  margin-top: 1rem;
}

.message-sources h5 {
  margin: 0 0 0.5rem 0;
  font-size: 0.8rem;
  font-weight: 600;
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
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.typing {
  opacity: 0.8;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 1rem 1.25rem;
  background: var(--bg-secondary);
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.chat-input {
  padding: 1.5rem 2rem;
  background: var(--bg-primary);
  border-top: 1px solid var(--border-color);
}

.input-container {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
}

.input-container .n-input {
  flex: 1;
}

.input-actions {
  flex-shrink: 0;
}

.input-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.5rem;
  text-align: center;
}

/* Scrollbar Styling */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

.chat-messages::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

/* Code styling in messages */
.message-text :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
}

.message.user .message-text :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}

/* Responsive Design */
@media (max-width: 768px) {
  .chat-container {
    height: calc(100vh - 60px);
    border-radius: 0;
  }

  .chat-header {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .chat-messages {
    padding: 1rem;
  }

  .message {
    max-width: 90%;
  }

  .welcome-content {
    flex-direction: column;
    text-align: center;
  }

  .input-container {
    flex-direction: column;
    gap: 0.75rem;
  }

  .input-actions {
    align-self: stretch;
  }

  .chat-input {
    padding: 1rem;
  }
}
</style>