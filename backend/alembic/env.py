"""Alembic 环境配置（支持 SQLite / PostgreSQL）。"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.database import Base
from app.models import *  # noqa: F401, F403 — import all models so they register on Base

# Alembic 配置对象
config = context.config

# 从 alembic.ini 配置 Python 日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 用于 autogenerate 支持的 MetaData
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emit SQL without connecting to DB)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Run migrations with a given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """使用 app 配置中的 DATABASE_URL 创建引擎并运行迁移。"""
    from app.config import settings

    url = settings.DATABASE_URL
    connectable = create_async_engine(url)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using async engine."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
