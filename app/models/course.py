"""
Course model
"""
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    short_description = Column(String(500), nullable=True)
    category = Column(String(100), nullable=False)  # Mathematics, English, IELTS, etc.
    duration_weeks = Column(Integer, nullable=False)
    hours_per_week = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    curriculum = Column(JSON, nullable=True)  # Store as JSON array
    requirements = Column(JSON, nullable=True)  # Store as JSON array
    target_audience = Column(String(500), nullable=True)
    max_students = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    thumbnail = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="course")

    def __repr__(self):
        return f"<Course {self.title}>"