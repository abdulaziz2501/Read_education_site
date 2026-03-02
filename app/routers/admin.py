"""
Admin routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.models.student import Student
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.certificate import Certificate
from app.schemas.user import User as UserSchema
from app.schemas.student import Student as StudentSchema, StudentCreate, StudentUpdate
from app.schemas.course import Course as CourseSchema, CourseCreate, CourseUpdate
from app.services.auth import AuthService

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


# Template routes
@router.get("/dashboard", response_class=Jinja2Templates.TemplateResponse)
async def admin_dashboard(
        request: Request,
        current_user: User = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
):
    """Admin dashboard"""
    # Get counts
    students_count = await db.scalar(select(func.count()).select_from(Student))
    courses_count = await db.scalar(select(func.count()).select_from(Course))
    enrollments_count = await db.scalar(select(func.count()).select_from(Enrollment))
    certificates_count = await db.scalar(select(func.count()).select_from(Certificate))

    # Get recent enrollments
    recent_enrollments = await db.execute(
        select(Enrollment)
        .order_by(Enrollment.created_at.desc())
        .limit(5)
    )

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": current_user,
            "stats": {
                "students": students_count or 0,
                "courses": courses_count or 0,
                "enrollments": enrollments_count or 0,
                "certificates": certificates_count or 0
            },
            "recent_enrollments": recent_enrollments.scalars().all()
        }
    )


@router.get("/students", response_class=Jinja2Templates.TemplateResponse)
async def admin_students(
        request: Request,
        current_user: User = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
):
    """Admin students page"""
    result = await db.execute(
        select(Student).order_by(Student.created_at.desc())
    )
    students = result.scalars().all()

    return templates.TemplateResponse(
        "admin/students.html",
        {
            "request": request,
            "user": current_user,
            "students": students
        }
    )


# API routes
@router.get("/api/students", response_model=List[StudentSchema])
async def get_students(
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
):
    """Get all students"""
    result = await db.execute(
        select(Student)
        .offset(skip)
        .limit(limit)
        .order_by(Student.created_at.desc())
    )
    return result.scalars().all()


@router.post("/api/students", response_model=StudentSchema, status_code=status.HTTP_201_CREATED)
async def create_student(
        student_data: StudentCreate,
        current_user: User = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
):
    """Create a new student"""
    # Check if student exists
    result = await db.execute(
        select(Student).where(Student.email == student_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this email already exists"
        )

    student = Student(
        **student_data.model_dump(),
        created_by=current_user.id
    )

    db.add(student)
    await db.commit()
    await db.refresh(student)

    return student


@router.get("/api/students/{student_id}", response_model=StudentSchema)
async def get_student(
        student_id: str,
        current_user: User = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
):
    """Get student by ID"""
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return student


@router.put("/api/students/{student_id}", response_model=StudentSchema)
async def update_student(
        student_id: str,
        student_data: StudentUpdate,
        current_user: User = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
):
    """Update student"""
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Update fields
    for field, value in student_data.model_dump(exclude_unset=True).items():
        setattr(student, field, value)

    await db.commit()
    await db.refresh(student)

    return student


@router.delete("/api/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
        student_id: str,
        current_user: User = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
):
    """Delete student"""
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    await db.delete(student)
    await db.commit()