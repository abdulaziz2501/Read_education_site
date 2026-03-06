from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# Many-to-many relationship table for User and Course
enrollment_table = Table(
    "enrollments",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("course_id", Integer, ForeignKey("courses.id"))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="student") # "admin" or "student"
    created_at = Column(DateTime, default=datetime.utcnow)

    enrollments = relationship("Course", secondary=enrollment_table, back_populates="students")
    certificates = relationship("Certificate", back_populates="student")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

    students = relationship("User", secondary=enrollment_table, back_populates="enrollments")
    certificates = relationship("Certificate", back_populates="course")

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    certificate_id = Column(String, unique=True, index=True)
    issue_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("User", back_populates="certificates")
    course = relationship("Course", back_populates="certificates")
