"""Async engine factory with production connection pooling settings.

Even for SQLite we configure pooling sensibly (WAL mode recommended for concurrency).
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

settings = get_settings()

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is not None:
        return _engine

    connect_args = {}
    if settings.is_sqlite:
        # Recommended for SQLite concurrency in the template
        connect_args = {"check_same_thread": False}

    _engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=settings.db_pool_recycle,
        pool_pre_ping=settings.db_pool_pre_ping,
        connect_args=connect_args,
    )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is not None:
        return _session_factory

    _session_factory = async_sessionmaker(
        bind=get_engine(),
        expire_on_commit=False,
        class_=AsyncSession,
    )
    return _session_factory


async def get_db_session() -> AsyncSession:
    """FastAPI dependency for DB session (per-request)."""
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def init_db() -> None:
    """Create tables if they don't exist (convenient for template/demo).

    For production-like setups run:
        uv run alembic upgrade head

    The create_all path remains for zero-config dev/CI.
    See alembic/ for migration scripts (Phase 2 addition).
    """
    from app.db.models import Base

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
