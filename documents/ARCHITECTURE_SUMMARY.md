# EduAgent Architecture Summary

## Current Implementation Status

### ✅ Chat Functionality - Direct Model Calls
**Location**: `backend/app/api/api_v1/endpoints/chat.py`

- **Architecture**: Direct SiliconFlow API calls
- **No Knowledge Base Integration**: Chat operates independently of LightRAG
- **Model**: `Pro/moonshotai/Kimi-K2-Instruct-0905` (configurable)
- **Endpoint**: `POST /api/chat/message`
- **Timeout**: 60 seconds
- **Simple System Prompt**: "You are a helpful AI assistant. Please provide clear and accurate responses."

**Features**:
- Clean, fast responses
- No dependency on knowledge base
- Configurable model selection
- Error handling with fallback messages
- Direct API communication

### ✅ Knowledge Base - LightRAG Integration
**Location**: `backend/app/services/knowledge_base.py` & `backend/app/api/api_v1/endpoints/knowledge.py`

- **Architecture**: LightRAG with SiliconFlow embeddings and LLM
- **Multi-Space Support**: Each space has independent RAG instance
- **Embedding Model**: `Qwen/Qwen3-Embedding-4B` (2560 dimensions)
- **LLM Model**: `Pro/moonshotai/Kimi-K2-Instruct-0905`
- **Query Modes**: naive, local, global, hybrid
- **Endpoint**: `POST /api/knowledge/query`
- **Timeout**: 30 seconds (with fallback)

**Features**:
- Document upload and indexing (PDF, DOCX, TXT, MD)
- Intelligent knowledge retrieval
- Multiple search modes
- Knowledge graph visualization
- Educational fallback responses
- Robust error handling

## Key Architectural Decisions

### 1. Separation of Concerns
- **Chat**: Direct model access for conversational AI
- **Knowledge**: RAG-powered retrieval for document-based queries

### 2. Resilience & Fallbacks
- **Timeout Protection**: Prevents system hangs
- **Educational Fallbacks**: Always provide helpful responses
- **Error Handling**: Graceful degradation

### 3. Performance Optimization
- **Async Processing**: Non-blocking operations
- **Configurable Timeouts**: Balance speed vs completeness
- **Multi-space Architecture**: Scalable knowledge organization

## API Endpoints Summary

### Chat Endpoints
```
POST /api/chat/message
{
  "message": "Your question here",
  "student_id": "user123",
  "model": "Pro/moonshotai/Kimi-K2-Instruct-0905"  // optional
}
```

### Knowledge Endpoints
```
POST /api/knowledge/query?space_name=default
{
  "question": "Your knowledge query",
  "mode": "hybrid",  // naive|local|global|hybrid
  "model": "moonshotai/Kimi-K2-Instruct-0905"  // optional
}

POST /api/knowledge/upload-document
GET /api/knowledge/documents
GET /api/knowledge/spaces
POST /api/knowledge/spaces
```

## Integration Benefits

1. **Fast Chat Responses**: Direct API calls without RAG overhead
2. **Intelligent Knowledge Retrieval**: LightRAG for complex document queries
3. **Scalable Architecture**: Independent scaling of chat vs knowledge services
4. **User Experience**: Appropriate tool for each use case
5. **Maintainability**: Clear separation makes debugging easier

## Usage Guidelines

### When to Use Chat
- General conversations
- Quick questions
- Creative tasks
- Immediate responses needed

### When to Use Knowledge Base
- Document-specific queries
- Research-based questions
- Complex multi-document analysis
- Educational content retrieval

This architecture provides the best of both worlds: fast, direct AI interactions for chat and powerful knowledge retrieval for document-based learning.