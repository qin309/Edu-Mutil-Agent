# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

EduAgent is a full-stack multimodal educational AI platform with two main components:

### Backend (FastAPI)
- **Location**: `backend/`
- **Server**: `main.py` (runs on port 8000)
- **Database**: SQLAlchemy with async SQLite (includes Users, Courses, Assignments, KnowledgePoints)
- **API Structure**: REST API under `/api/` prefix (routers include auth, users, assignments, knowledge)
- **Authentication**: JWT-based with OAuth2 patterns
- **Key Services**:
  - Document scanning (OpenCV)
  - AI analysis (OpenRouter API + Grok models)
  - Knowledge base (LightRAG)
  - Multimodal agents for assignment analysis

### Frontend (Vue 3)
- **Location**: `frontend/`
- **Server**: Vite dev server (runs on port 3001)
- **Framework**: Vue 3 + TypeScript + Naive UI components
- **State Management**: Pinia stores with authentication
- **API Communication**: Axios with `/api` proxy to backend
- **Routing**: Vue Router with authentication guards

### Architecture Flow
```
Frontend (port 3001) ←→ Vite Proxy (/api/* → http://localhost:8000/api/*) ←→ FastAPI Backend (port 8000)
                                                                                                  ↓
                                                                                            Database + AI Services
```

## Development Workflow

### Starting Development Servers
Both servers must run simultaneously for development:

```bash
# Terminal 1: Backend API server
cd backend && python main.py

# Terminal 2: Frontend dev server
cd frontend && npm run dev
```

### Key Development Commands

#### Frontend
- `npm run dev` - Start Vite development server (port 3001)
- `npm run build` - Type-check with TypeScript and build production bundle
- `npm run lint` - ESLint with Vue support and auto-fix
- `npm run test` - Run Vitest unit tests
- `npm run preview` - Preview production build

#### Backend
- `python main.py` - Start FastAPI server with uvicorn (port 8000, auto-reload enabled)
- `python -m pytest` - Run test suite with pytest (when implemented)
- `pip install -r requirements.txt` - Install Python dependencies
- `uvicorn main:app --reload --host 0.0.0.0 --port 8000` - Alternative server command

### API Development Insights

#### Authentication Flow
- **Frontend stores**: Use `auth.ts` Pinia store for login/register/logout
- **Backend endpoints**: `/api/auth/register`, `/api/auth/test-login` (returns user data directly for frontend)
- **Frontend proxy**: Routes `/api/*` to backend automatically (configured in `vite.config.ts`)
- **JWT handling**: Automatic header injection via axios interceptors
- **Login request format**: `{"email": "user@example.com", "password": "password"}`

#### Database Management
- **Models**: Located in `backend/app/models/` (User, Course, Assignment, KnowledgePoint)
- **Migration**: Automatic via SQLAlchemy lifecycle (create_all on startup)
- **Development DB**: SQLite (`eduagent.db`)
- **Database Relationships**: User → Courses → Assignments → KnowledgePoints (hierarchical structure)

#### AI Integration
- **Dual API Architecture**:
  - **OpenRouter API**: Used for chat and general AI features (default model: `deepseek-ai/DeepSeek-V3.1-Terminus`)
  - **SiliconFlow API**: Required for LightRAG knowledge base (Qwen3-Embedding-4B + Qwen3-Next-80B)
- **Model Configuration**:
  - Default model set in `backend/app/core/config.py` as `DEFAULT_MODEL`
  - All AI endpoints support optional `model` parameter to override default
  - Chat API: `{"message": "...", "student_id": "...", "model": "optional-model-name"}`
  - Agent methods: Pass `model="model-name"` parameter to any analysis function
- **Configuration**: Set both `OPENROUTER_API_KEY` and `SILICONFLOW_API_KEY` in `.env`
- **Agents**: Custom multimodal agents in `backend/app/agents/`
- **Document Processing**: OpenCV-based skew correction in `backend/app/services/doc_scanner.py`
- **⚠️ Security Note**: Remove hardcoded API key in `main.py` line 86 before production deployment

### Debugging Tips

#### API Communication
- Frontend calls like `api.post('/auth/register')` automatically become `http://localhost:3001/api/auth/register` → `http://localhost:8000/api/auth/register` (via proxy)
- Check browser Network tab for failed requests
- Verify both servers are running on correct ports

#### Authentication Issues
- Check localStorage for `eduagent_token` and `eduagent_user`
- Routes with `meta: { requiresAuth: true }` need authentication
- Use `/api/auth/test-login` for login (returns user object directly for frontend)

#### Database Issues
- Backend automatically creates tables on startup
- Database file: `backend/eduagent.db`
- Reset database by deleting the .db file and restarting backend

### File Structure Patterns

#### Frontend Architecture
- **Views**: Page-level components in `src/views/`
- **Components**: Reusable components in `src/components/`
- **Stores**: Pinia state management in `src/stores/`
- **Services**: API client (`src/services/api.ts`)
- **Types**: TypeScript interfaces as needed

#### Backend Architecture
- **API Routes**: `app/api/api_v1/endpoints/` (auth, users, assignments, knowledge)
- **Business Logic**: `app/services/` (user operations, document processing, assignment workflow)
- **Database**: `app/models/` (SQLAlchemy models), `app/db/session.py`
- **Core Config**: `app/core/config.py` (API keys, app settings)

### Common Modification Patterns

#### Adding New API Endpoints
1. Create new endpoint file in `backend/app/api/api_v1/endpoints/`
2. Import and include router in `backend/app/api/api_v1/api.py`
3. Add frontend API calls through `/api` proxy prefix

#### Adding New Frontend Pages
1. Create component in `src/views/`
2. Add route in `src/router/index.ts` with appropriate auth meta
3. Add navigation links in `src/App.vue`

#### Adding New AI Capabilities
1. Extend agents in `backend/app/agents/`
2. Add new endpoints for analysis requests
3. Integration through multimodal analysis pipeline

### Security & Configuration
- **Environment**: Set both `OPENROUTER_API_KEY` and `SILICONFLOW_API_KEY` in backend `.env` file
  - `OPENROUTER_API_KEY`: For chat/general AI features
  - `SILICONFLOW_API_KEY`: Required for knowledge base functionality (embeddings + LLM)
- **CORS**: Configured for localhost development (ports 3000, 3001, 8080)
- **Authentication**: JWT tokens stored in localStorage
- **API Security**: All endpoints behind token authentication
- **Platform Notes**: Project uses Windows paths (`g:\mult_eduagent\EduAgent`); adjust commands for Unix/Linux systems if needed

### Testing the System
1. Start both backend and frontend servers
2. Access `http://localhost:3001` (frontend)
3. Register/login → Dashboard
4. Check backend logs at `http://localhost:8000/docs` for API documentation
5. Verify AI features work (may need valid API keys)

### Code Quality Commands
- **Type Checking**: `cd frontend && vue-tsc` (TypeScript type checking)
- **Frontend Linting**: `cd frontend && npm run lint` (ESLint + Prettier)
- **Code Formatting**: Prettier included in ESLint (automatic via `npm run lint`)

### Integration Points
- **Frontend ↔ Backend**: `/api` proxy routes all frontend API calls (vite.config.ts)
- **Backend ↔ AI Services**:
  - OpenRouter for chat/general AI (main.py)
  - SiliconFlow for knowledge base embeddings and LLM (knowledge_base.py)
- **Backend ↔ Database**: SQLAlchemy async connections (app/db/session.py)
- **Document Processing**: File uploads through `/api` endpoints to backend processing
- **LightRAG Integration**: Multi-space knowledge base with separate storage per space (`uploads/knowledge_spaces/{space_name}/`)