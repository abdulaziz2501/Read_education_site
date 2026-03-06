"""
Public routes for the website
"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.models.course import Course
from app.models.student import Student
from app.schemas.student import StudentCreate
from app.services.email import EmailService

router = APIRouter(tags=["public"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Home page"""
    # Get featured courses
    result = await db.execute(
        select(Course).where(Course.is_active == True, Course.is_featured == True).limit(3)
    )
    featured_courses = result.scalars().all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "featured_courses": featured_courses,
            "page_title": "School of Excellence - Quality Education"
        }
    )


@router.get("/courses", response_class=HTMLResponse)
async def courses_page(
        request: Request,
        category: Optional[str] = None,
        db: AsyncSession = Depends(get_db)
):
    """Courses listing page"""
    query = select(Course).where(Course.is_active == True)

    if category:
        query = query.where(Course.category == category)

    result = await db.execute(query)
    courses = result.scalars().all()

    return templates.TemplateResponse(
        "courses.html",
        {
            "request": request,
            "courses": courses,
            "selected_category": category,
            "page_title": "Our Courses - School of Excellence"
        }
    )


@router.get("/courses/{slug}", response_class=HTMLResponse)
async def course_detail_page(request: Request, slug: str, db: AsyncSession = Depends(get_db)):
    """Course detail page"""
    result = await db.execute(
        select(Course).where(Course.slug == slug, Course.is_active == True)
    )
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return templates.TemplateResponse(
        "course-detail.html",
        {
            "request": request,
            "course": course,
            "page_title": f"{course.title} - School of Excellence"
        }
    )


@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    """About page"""
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "page_title": "About Us - School of Excellence"
        }
    )


@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    """Contact page"""
    return templates.TemplateResponse(
        "contact.html",
        {
            "request": request,
            "page_title": "Contact Us - School of Excellence"
        }
    )


@router.post("/contact/submit")
async def contact_submit(
        name: str = Form(...),
        email: str = Form(...),
        message: str = Form(...),
        db: AsyncSession = Depends(get_db)
):
    """Handle contact form submission"""
    try:
        # Send email notification
        email_service = EmailService()
        await email_service.send_contact_notification(name, email, message)

        return JSONResponse(
            status_code=200,
            content={"message": "Thank you for contacting us. We'll get back to you soon."}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "Failed to send message. Please try again."}
        )