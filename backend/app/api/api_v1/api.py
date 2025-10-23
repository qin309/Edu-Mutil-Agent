"""
Main API router configuration
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, assignments, knowledge, chat

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])  # Re-added proper chat router