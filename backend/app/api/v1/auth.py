"""认证端点：注册和登录。"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.user import User, UserRole
from app.schemas.user import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: UserRegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """注册新用户账号。"""
    client_ip = request.client.host if request.client else "unknown"
    logger.info("Register request from {}: username={}, email={}", client_ip, body.username, body.email)

    # 检查用户名唯一性
    result = await db.execute(select(User).where(User.username == body.username))
    if result.scalar_one_or_none():
        logger.warning("Register failed from {}: username '{}' already taken", client_ip, body.username)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    # 检查邮箱唯一性
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        logger.warning("Register failed from {}: email '{}' already registered", client_ip, body.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # 创建用户
    user = User(
        username=body.username,
        email=body.email,
        hashed_password=hash_password(body.password),
        role=UserRole(body.role),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    logger.info("User registered successfully: username={}, email={}", user.username, user.email)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    body: UserLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """认证用户并返回 JWT Token。"""
    client_ip = request.client.host if request.client else "unknown"
    logger.info("Login request from {}: username={}", client_ip, body.username)

    result = await db.execute(
        select(User).where(User.username == body.username)
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(body.password, user.hashed_password):
        logger.warning("Login failed from {}: invalid credentials for username={}", client_ip, body.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_active:
        logger.warning("Login failed from {}: account '{}' is deactivated", client_ip, body.username)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    logger.info("User logged in successfully: username={}", body.username)
    return TokenResponse(
        access_token=create_access_token(user_id=str(user.id)),
        refresh_token=create_refresh_token(user_id=str(user.id)),
    )
