"""FastAPI 应用入口点。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1.router import api_v1_router
from app.config import settings


async def _seed_admin_user():
    """初始化默认管理员账户（admin/admin），仅本地开发使用。"""
    from sqlalchemy import select

    from app.database import async_session_factory
    from app.models.user import User, UserRole
    from app.services.auth import hash_password

    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none() is None:
            user = User(
                username="admin",
                email="admin@smarthire.local",
                hashed_password=hash_password("admin"),
                role=UserRole.HR,
                is_active=True,
            )
            session.add(user)
            await session.commit()
            logger.info("Default admin user created (admin/admin)")
        else:
            logger.debug("Default admin user already exists, skipped")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """处理应用的启动和关闭。"""
    logger.info(f"Starting {settings.APP_NAME}...")

    # 初始化默认管理员
    if settings.SEED_ADMIN:
        await _seed_admin_user()

    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载 API v1 路由
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """健康检查端点。"""
    return {"status": "ok", "app": settings.APP_NAME}
