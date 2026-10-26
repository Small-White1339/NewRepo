"""FastAPI dependency injection utilities."""

from uuid import UUID

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency: extract and verify current user from JWT bearer token."""
    if credentials is None:
        logger.warning("Authentication failed: no bearer token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id_str: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")
        if user_id_str is None or token_type != "access":
            logger.warning(
                "Authentication failed: invalid token payload (missing sub or wrong type)"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        user_id = UUID(user_id_str)
        logger.debug("Token decoded successfully: sub={}", user_id_str)
    except (JWTError, ValueError) as e:
        logger.warning("Authentication failed: JWT decode error: {}", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        logger.warning("Authentication failed: user {} not found or inactive", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    logger.debug("User authenticated: user_id={}, username={}", user.id, user.username)
    return user


async def get_current_hr(current_user: User = Depends(get_current_user)) -> User:
    """招聘业务写操作仅允许 HR 角色。"""
    if current_user.role != UserRole.HR:
        raise HTTPException(status_code=403, detail="此操作仅限招聘人员。")
    return current_user


async def get_current_job_seeker(current_user: User = Depends(get_current_user)) -> User:
    """求职功能仅允许求职者账号访问。"""
    if current_user.role != UserRole.JOB_SEEKER:
        raise HTTPException(status_code=403, detail="请使用求职者账号访问。")
    return current_user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Dependency: get current user if token provided, otherwise None."""
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


async def get_current_user_from_query(
    token: str = Query("", description="JWT token (用于文件预览等无法带 Header 的场景)"),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """从 Bearer header 或 Query ?token= 中获取 JWT 验证用户。"""
    if credentials:
        return await get_current_user(credentials, db)
    if token:
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        return await get_current_user(creds, db)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
