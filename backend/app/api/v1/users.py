"""User management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdateRequest

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Get the authenticated user's profile."""
    logger.debug(
        "User profile queried: user_id={}, username={}", current_user.id, current_user.username
    )
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    body: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the authenticated user's profile."""
    update_data = body.model_dump(exclude_unset=True)
    logger.info(
        "User profile update requested: user_id={}, fields={}",
        current_user.id,
        list(update_data.keys()),
    )

    if "username" in update_data and update_data["username"] != current_user.username:
        result = await db.execute(select(User).where(User.username == update_data["username"]))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

    if "email" in update_data and update_data["email"] != current_user.email:
        result = await db.execute(select(User).where(User.email == update_data["email"]))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.flush()
    await db.refresh(current_user)
    logger.info(
        "User profile updated: user_id={}, fields_changed={}",
        current_user.id,
        list(update_data.keys()),
    )
    return current_user
