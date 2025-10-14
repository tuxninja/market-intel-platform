"""
User schemas for authentication and profile management.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr


class UserCreate(UserBase):
    """
    Schema for user registration.

    Attributes:
        email: User email address
        password: Plain text password (will be hashed)
        full_name: Optional full name
    """

    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """
    Schema for user login.

    Attributes:
        email: User email address
        password: Plain text password
    """

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """
    Schema for user response.

    Attributes:
        id: User ID
        email: User email
        subscription_tier: Current subscription tier
        is_active: Account active status
        is_verified: Email verification status
        full_name: User's full name
        created_at: Account creation timestamp
    """

    id: int
    subscription_tier: str
    is_active: bool
    is_verified: bool
    full_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """
    Schema for JWT token response.

    Attributes:
        access_token: JWT access token
        refresh_token: JWT refresh token
        token_type: Token type (always "bearer")
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Schema for token payload data.

    Attributes:
        user_id: User ID from token
        email: User email from token
    """

    user_id: Optional[int] = None
    email: Optional[str] = None
