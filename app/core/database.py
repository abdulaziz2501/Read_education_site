"""
Database configuration and session management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from typing import AsyncGenerator

from app.core.config import settings

# SQLite uchun maxsus sozlamalar
engine_args = {
    "echo": settings.ENVIRONMENT == "development",
    "future": True,
    "poolclass": StaticPool,  # SQLite uchun StaticPool ishlatiladi
}

# SQLite uchun maxsus parametrlar
if settings.DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    **engine_args
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()