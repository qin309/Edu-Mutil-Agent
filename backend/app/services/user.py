"""
User service for CRUD operations
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_password_hash, verify_password
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """
    Service for user operations
    """

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[UserModel]:
        """
        Get user by email
        """
        result = await db.execute(select(UserModel).where(UserModel.email == email))
        return result.scalars().first()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[UserModel]:
        """
        Get user by ID
        """
        result = await db.execute(select(UserModel).where(UserModel.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, user_data: UserCreate) -> UserModel:
        """
        Create new user
        """
        hashed_password = get_password_hash(user_data.password)
        db_user = UserModel(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def update(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[UserModel]:
        """
        Update user information
        """
        result = await db.execute(select(UserModel).where(UserModel.id == user_id))
        db_user = result.scalars().first()

        if not db_user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            del update_data["password"]

        for field, value in update_data.items():
            setattr(db_user, field, value)

        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str) -> Optional[UserModel]:
        """
        Authenticate user with email and password
        """
        user = await UserService.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user