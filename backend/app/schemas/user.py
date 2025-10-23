"""
User schemas for API requests and responses
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """
    Base user schema with common fields
    """
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """
    Schema for user creation requests
    """
    password: str
    confirm_password: str


class UserUpdate(UserBase):
    """
    Schema for user update requests
    """
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """
    Base schema for user stored in database
    """
    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


class User(UserInDBBase):
    """
    Schema for user responses
    """
    pass


class UserInDB(UserInDBBase):
    """
    Schema for user stored in database (internal use)
    """
    hashed_password: str