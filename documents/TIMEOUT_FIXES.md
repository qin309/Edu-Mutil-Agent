# Knowledge Query Timeout Fixes

## Problem
Frontend queries to the knowledge base were timing out after 30 seconds with the error:
```
AxiosError: timeout of 30000ms exceeded
```

## Root Cause
LightRAG knowledge queries can take longer than 30 seconds, especially for:
- Complex queries requiring extensive search
- First-time queries that need storage initialization
- Large knowledge bases with many documents
- Queries involving vector similarity search and LLM processing

## Applied Fixes

### 1. Frontend Timeout Increases

#### General API Timeout
**File**: `frontend/src/services/api.ts`
```typescript
// Before: timeout: 30000 (30 seconds)
// After: timeout: 60000 (60 seconds)
```

#### Knowledge Query Specific Timeout
**File**: `frontend/src/views/Knowledge.vue`
```typescript
const response = await api.post('/knowledge/query', requestData, {
  params: { space_name: currentSpace.value },
  timeout: 120000 // 120 seconds (2 minutes) for LightRAG processing
})
```

### 2. Backend Optimizations

#### Server Configuration
**File**: `backend/main.py`
```python
uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=8000,
    reload=True,
    timeout_keep_alive=120,  # Increased keep-alive timeout
    timeout_graceful_shutdown=30
)
```

#### Performance Monitoring
**File**: `backend/app/services/knowledge_base.py`
- Added detailed timing logs for query performance analysis
- Storage initialization timing
- LightRAG query execution timing
- Total query time tracking

### 3. User Experience Improvements

#### Progress Indicators
**File**: `frontend/src/views/Knowledge.vue`
- Progress messages every 10 seconds for long queries
- Better error messages for timeout scenarios
- Query timing information in console logs

#### Error Handling
- Specific timeout error detection (`ECONNABORTED`)
- User-friendly timeout messages
- Suggestions for simpler queries

## Timeout Settings Summary

| Component | Setting | Timeout |
|-----------|---------|---------|
| General API | `api.ts` | 60 seconds |
| Knowledge Query | `Knowledge.vue` | 120 seconds |
| Server Keep-Alive | `main.py` | 120 seconds |

## Performance Expectations

### Normal Query Times
- Simple queries: 5-15 seconds
- Complex queries: 15-60 seconds
- First-time queries: 20-90 seconds (due to initialization)

### Timeout Triggers
- Queries taking >120 seconds will timeout
- Network connectivity issues
- Backend server not running
- LightRAG processing errors

## Troubleshooting

### If Queries Still Timeout
1. **Check Backend Status**: Ensure server is running on port 8000
2. **Simplify Query**: Try shorter, more specific questions
3. **Check Console**: Look for performance timing logs
4. **Restart Backend**: Clear any stuck processes

### Performance Optimization Tips
1. Use specific knowledge spaces
2. Ask focused questions rather than broad queries
3. Ensure documents are properly indexed
4. Monitor backend logs for bottlenecks

## Testing
Use `test_query_performance.py` to:
- Test query response times
- Identify performance bottlenecks
- Verify timeout fixes work correctly

## Future Improvements
1. Query result caching
2. Streaming responses for real-time feedback
3. Query complexity analysis
4. Background processing for large queries