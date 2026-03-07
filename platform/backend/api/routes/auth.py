"""Authentication endpoints: login, register, me."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy import select

from api.schemas.auth import LoginRequest, LoginResponse, LoginUserInfo, UserCreate, UserResponse
from api.schemas.common import APIResponse
from core.config import get_settings
from core.database import get_db
from core.security import create_access_token, get_password_hash, verify_password
from middleware.auth import get_current_user
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
settings = get_settings()


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(
    form: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> APIResponse[LoginResponse]:
    """Authenticate user and return JWT token with user info."""
    result = await db.execute(select(User).where(User.username == form.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token(subject=user.id)
    return APIResponse(
        data=LoginResponse(
            accessToken=token,
            expiresIn=settings.jwt_expire_minutes * 60,
            user=LoginUserInfo(
                id=str(user.id),
                username=user.username,
                role=user.role,
                displayName=user.username,
            ),
        ),
    )


@router.post("/register", response_model=APIResponse[UserResponse])
async def register(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> APIResponse[UserResponse]:
    """Register a new user."""
    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return APIResponse(data=UserResponse.model_validate(user))


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_me(
    user: Annotated[User, Depends(get_current_user)],
) -> APIResponse[UserResponse]:
    """Get current authenticated user."""
    return APIResponse(data=UserResponse.model_validate(user))
