"""Pydantic schemas for User CRUD operations."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

# ---------- Request Schemas ----------

class UserRegisterRequest(BaseModel):
    """User registration request body."""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, max_length=128, description="Password (plain text)")
    role: str = Field(default="JOB_SEEKER", pattern="^(HR|JOB_SEEKER)$")


class UserLoginRequest(BaseModel):
    """User login request body."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password (plain text)")


class UserUpdateRequest(BaseModel):
    """User profile update request body."""
    username: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = None


# ---------- Response Schemas ----------

class UserResponse(BaseModel):
    """User detail response."""
    id: UUID
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # user_id
    exp: int
    type: str = "access"
