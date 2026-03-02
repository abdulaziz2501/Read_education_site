"""
Database models initialization
"""
from app.models.user import User
from app.models.student import Student
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.certificate import Certificate
__all__ = [
    "User",
    "Student",
    "Course",
    "Enrollment",
    "Certificate",
]