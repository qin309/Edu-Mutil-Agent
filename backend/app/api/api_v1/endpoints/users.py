"""
User management endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.deps import get_current_active_user, get_current_user
from app.models.user import User as UserModel
from app.schemas.user import User, UserUpdate
from app.services.user import UserService

router = APIRouter()


@router.get("/", response_model=List[User])
async def read_users(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """
    Get all users (admin only)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # For simplicity, just return the current user
    # In production, you'd want proper admin user listing
    users = [await UserService.get_by_id(db, current_user.id)]
    return [User.from_orm(user) for user in users if user]


@router.put("/me", response_model=User)
async def update_user_me(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
) -> User:
    """
    Update current user
    """
    user = await UserService.update(db, current_user.id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return User.from_orm(user)


@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> User:
    """
    Get user by ID
    """
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Users can only view themselves unless they're admin
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return User.from_orm(user)