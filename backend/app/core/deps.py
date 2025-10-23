"""
Dependency injection functions
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import verify_token
from app.db.session import get_db
from app.models.user import User as UserModel
from app.services.user import UserService

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> UserModel:
    """
    Get current authenticated user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = verify_token(token)
    if user_id is None:
        raise credentials_exception

    user = await UserService.get_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Get current active user
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user