"""
Main application entry point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.database import engine
from app.models import Base
from app.routers import public, auth, admin, students, courses, certificates, verification
from app.utils.middleware import LoggingMiddleware, RateLimitMiddleware
from app.utils.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting up...")
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Shutdown
    logger.info("Shutting down...")
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Professional School Management System",
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# Setup middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(public.router, tags=["public"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(certificates.router, prefix="/api/certificates", tags=["certificates"])
app.include_router(verification.router, prefix="/verify", tags=["verification"])


@app.get("/")
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/courses")
async def courses_page(request: Request):
    """Courses listing page"""
    return templates.TemplateResponse("courses.html", {"request": request})


@app.get("/courses/{course_id}")
async def course_detail(request: Request, course_id: str):
    """Course detail page"""
    return templates.TemplateResponse("course-detail.html", {
        "request": request,
        "course_id": course_id
    })


@app.get("/about")
async def about_page(request: Request):
    """About page"""
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/contact")
async def contact_page(request: Request):
    """Contact page"""
    return templates.TemplateResponse("contact.html", {"request": request})


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Custom HTTP exception handler"""
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request},
            status_code=404
        )
    return templates.TemplateResponse(
        "errors/500.html",
        {"request": request},
        status_code=exc.status_code
    )


@app.get("/sitemap.xml")
async def sitemap():
    """Serve sitemap.xml"""
    from fastapi.responses import FileResponse
    return FileResponse("app/static/sitemap.xml")


@app.get("/robots.txt")
async def robots():
    """Serve robots.txt"""
    from fastapi.responses import FileResponse
    return FileResponse("app/static/robots.txt")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )