"""Authentication schemas."""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request body."""

    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1)


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserCreate(BaseModel):
    """User registration request."""

    username: str = Field(..., min_length=2, max_length=64)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = Field(default="viewer", pattern="^(admin|trainer|engineer|viewer)$")


class UserResponse(BaseModel):
    """User response (no password)."""

    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True
