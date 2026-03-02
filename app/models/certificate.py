"""
Certificate model for issued certificates
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    certificate_id = Column(String(100), unique=True, nullable=False, index=True)
    student_id = Column(String(36), ForeignKey("students.id"), nullable=False)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    enrollment_id = Column(String(36), ForeignKey("enrollments.id"), nullable=False, unique=True)
    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    grade = Column(String(10), nullable=True)
    qr_code = Column(Text, nullable=True)  # Store QR code as base64 or path
    pdf_path = Column(String(500), nullable=True)
    is_valid = Column(Boolean, default=True)
    metadata = Column(Text, nullable=True)  # JSON string for additional data
    issued_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="certificates")
    course = relationship("Course", back_populates="certificates")
    enrollment = relationship("Enrollment", back_populates="certificate")
    issued_by_user = relationship("User", back_populates="certificates")

    def __repr__(self):
        return f"<Certificate {self.certificate_id}>"