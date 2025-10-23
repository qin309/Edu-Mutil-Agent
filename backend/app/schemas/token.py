"""
Token schemas for authentication
"""
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """
    Token response schema
    """
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """
    Token payload schema
    """
    sub: Optional[int] = None