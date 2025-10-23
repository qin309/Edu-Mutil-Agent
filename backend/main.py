"""
EduAgent Backend API
Multi-modal educational agent platform
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.api_v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url="/api/openapi.json",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 routers
app.include_router(api_router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    print("DEBUG: Root endpoint called from main.py")
    return {
        "message": "Mult-Agent-Edu Platform API",
        "version": "1.0.0",
        "status": "running",
        "description": "Multi-agent educational service platform",
        "debug": "main.py is running on port 8000"
    }

# Test API routes
@app.get("/api/test")
async def api_test():
    return {"message": "API route works"}

if __name__ == "__main__":
    print("Starting EduAgent backend on port 8000...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        timeout_keep_alive=120,  # Increased keep-alive timeout
        timeout_graceful_shutdown=30
    )