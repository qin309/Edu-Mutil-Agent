"""
Authentication schemas
"""
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """
    Login request schema
    """
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    """
    Password reset request schema
    """
    email: EmailStr


class PasswordReset(BaseModel):
    """
    Password reset schema
    """
    new_password: str
    confirm_new_password: str
    token: str