# Knowledge Base Query Error Troubleshooting

## Problem Identified
Frontend knowledge queries are failing with network errors:
```
AxiosError: Network Error
net::ERR_EMPTY_RESPONSE
Failed to load resource: net::ERR_EMPTY_RESPONSE
```

## Root Cause Analysis
The `net::ERR_EMPTY_RESPONSE` error indicates that the backend server is not responding at all to the knowledge query requests. This could be due to:

1. **Authentication Issues**: Knowledge endpoints require authentication
2. **Server Crash**: Backend might be crashing on knowledge queries  
3. **Import/Initialization Errors**: Knowledge base service might not be initializing
4. **Timeout Issues**: Long-running LightRAG operations might be timing out

## Applied Fixes

### 1. Temporarily Disabled Authentication
```python
# In knowledge.py endpoints
# current_user: User = Depends(get_current_user)  # Temporarily disabled for debugging
```

### 2. Added Debug Logging
```python
# Enhanced error handling and logging in query endpoint
print(f"[API] Received knowledge query: {query.question[:50]}...")
print(f"[API] Knowledge base available: {knowledge_base.is_available(space_name)}")
```

### 3. Enhanced Error Handling
```python
# Better exception handling in knowledge endpoints
try:
    # ... endpoint logic
except Exception as e:
    print(f"[API] ERROR: {e}")
    traceback.print_exc()
    # Return fallback response
```

## Testing Steps

### 1. Test Basic Backend Connectivity
```bash
python test_knowledge_endpoint.py
```

### 2. Check Backend Logs
- Start backend: `python main.py`
- Look for error messages during startup
- Check for LightRAG initialization errors

### 3. Test Individual Endpoints
```bash
# Test status endpoint
curl http://localhost:8000/api/knowledge/status

# Test spaces endpoint  
curl http://localhost:8000/api/knowledge/spaces

# Test query endpoint
curl -X POST http://localhost:8000/api/knowledge/query?space_name=test \
  -H "Content-Type: application/json" \
  -d '{"question":"test","mode":"hybrid"}'
```

## Expected Issues and Solutions

### Issue: Authentication Errors (401)
**Solution**: Authentication temporarily disabled for debugging

### Issue: Server Crashes on Query
**Symptoms**: Backend stops responding
**Check**: 
- LightRAG dependency issues
- SiliconFlow API key problems
- Memory/resource issues

### Issue: Import Errors
**Symptoms**: Knowledge base service not available
**Check**:
- LightRAG installation: `pip install lightrag-hku`
- Python dependencies
- Import errors in knowledge_base.py

### Issue: LightRAG Initialization Failures
**Symptoms**: Knowledge base shows as not available
**Check**:
- SiliconFlow API key configuration
- Vector database file permissions
- Embedding model configuration

## Debugging Checklist

### Backend Startup
- [ ] Backend starts without errors
- [ ] No import errors in console
- [ ] Knowledge base service initializes
- [ ] Default space creates successfully

### API Endpoints
- [ ] `/api/knowledge/status` returns 200
- [ ] `/api/knowledge/spaces` returns 200  
- [ ] `/api/knowledge/query` returns 200 (not crashes)

### LightRAG Integration
- [ ] Embedding function works
- [ ] LLM function works
- [ ] Vector database accessible
- [ ] Query processing works

## Recovery Steps

### If Backend Crashes on Query
1. Check backend logs for error details
2. Verify SiliconFlow API key is valid
3. Clear vector database: `rm -rf uploads/knowledge_spaces/*/vdb_*.json`
4. Restart backend

### If Authentication Issues
1. Re-enable authentication after debugging
2. Verify JWT token generation
3. Check frontend token handling

### If Import/Initialization Issues
1. Reinstall LightRAG: `pip install lightrag-hku`
2. Check Python environment
3. Verify configuration files

## Monitoring

### Backend Logs to Watch
```
[RAG Init] Initializing LightRAG for knowledge space: ...
[API] Received knowledge query: ...
[Query] Starting query for space '...'
```

### Error Patterns
```
ImportError: No module named 'lightrag'
[RAG Init] ERROR: LightRAG initialization failed
[API] ERROR: knowledge_base is None
```

## Next Steps
1. Run test script to identify specific failure point
2. Check backend logs during query attempts
3. Re-enable authentication once core issue is resolved
4. Implement proper error recovery mechanisms