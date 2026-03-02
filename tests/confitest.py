"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models.user import User
from app.models.student import Student
from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.certificate import Certificate
from app.core.security import get_password_hash, create_access_token

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests"""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()
        await session.close()

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator:
    """Create test client"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create admin user"""
    user = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        is_superuser=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def admin_token(admin_user: User) -> str:
    """Create admin token"""
    return create_access_token(str(admin_user.id))

@pytest.fixture
async def test_student(db_session: AsyncSession, test_user: User) -> Student:
    """Create test student"""
    student = Student(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+1234567890",
        created_by=test_user.id
    )
    db_session.add(student)
    await db_session.commit()
    await db_session.refresh(student)
    return student

@pytest.fixture
async def test_course(db_session: AsyncSession) -> Course:
    """Create test course"""
    course = Course(
        title="Python Programming",
        slug="python-programming",
        description="Learn Python from scratch",
        short_description="Python course",
        category="Programming",
        duration_weeks=12,
        hours_per_week=4,
        price=299.99,
        is_active=True
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)
    return course

@pytest.fixture
async def test_enrollment(
    db_session: AsyncSession,
    test_student: Student,
    test_course: Course
) -> Enrollment:
    """Create test enrollment"""
    enrollment = Enrollment(
        student_id=test_student.id,
        course_id=test_course.id,
        status=EnrollmentStatus.ACTIVE,
        progress=50
    )
    db_session.add(enrollment)
    await db_session.commit()
    await db_session.refresh(enrollment)
    return enrollment

@pytest.fixture
async def test_certificate(
    db_session: AsyncSession,
    test_student: Student,
    test_course: Course,
    test_enrollment: Enrollment,
    admin_user: User
) -> Certificate:
    """Create test certificate"""
    from app.services.certificate import CertificateService

    service = CertificateService(db_session)

    certificate_data = {
        "student_id": test_student.id,
        "course_id": test_course.id,
        "enrollment_id": test_enrollment.id,
        "grade": "A",
        "issued_by": admin_user.id
    }

    certificate = await service.create_certificate(certificate_data)
    return certificate