#!/usr/bin/env python3
"""
Seed admin user script
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.models.user import User
from app.core.security import get_password_hash


async def seed_admin():
    """Create admin user if not exists"""
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(lambda x: None)  # Test connection

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Check if admin exists
        result = await session.execute(
            select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
        )
        admin = result.scalar_one_or_none()

        if not admin:
            print("Creating admin user...")
            admin = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                username="admin",
                full_name="System Administrator",
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                is_superuser=True,
                is_active=True
            )
            session.add(admin)
            await session.commit()
            print(f"Admin user created successfully: {settings.FIRST_SUPERUSER_EMAIL}")
        else:
            print("Admin user already exists")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_admin())