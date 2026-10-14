"""Async SQLAlchemy engine, session factory, and Base."""

from collections.abc import AsyncGenerator

from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

def _mask_db_url(url: str) -> str:
    """Mask the password in a database URL for safe logging."""
    if "://" not in url:
        return url
    scheme, rest = url.split("://", 1)
    if "@" not in rest:
        return url
    userinfo, host = rest.rsplit("@", 1)
    if ":" in userinfo:
        userinfo = userinfo.split(":")[0] + ":****"
    return f"{scheme}://{userinfo}@{host}"


_is_sqlite = settings.DATABASE_URL.startswith("sqlite")
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    **(dict(pool_size=10, max_overflow=20) if not _is_sqlite else {}),
)
logger.info("Database engine created: url={}", _mask_db_url(settings.DATABASE_URL))

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
logger.debug("Database session factory created")


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an async database session."""
    async with async_session_factory() as session:
        logger.debug("Database session started")
        try:
            yield session
            await session.commit()
            logger.debug("Database session committed and closed")
        except Exception:
            await session.rollback()
            logger.debug("Database session rolled back and closed")
            raise
