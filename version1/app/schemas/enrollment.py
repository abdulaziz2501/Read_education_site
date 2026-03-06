"""
Enrollment schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

class EnrollmentStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"
    ON_HOLD = "on_hold"

class EnrollmentBase(BaseModel):
    student_id: str
    course_id: str
    status: EnrollmentStatus = EnrollmentStatus.PENDING
    progress: int = Field(0, ge=0, le=100)
    notes: Optional[str] = None

class EnrollmentCreate(EnrollmentBase):
    start_date: Optional[datetime] = None

class EnrollmentUpdate(BaseModel):
    status: Optional[EnrollmentStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    end_date: Optional[datetime] = None
    grade: Optional[str] = None
    notes: Optional[str] = None

class EnrollmentInDB(EnrollmentBase):
    id: str
    enrollment_date: datetime
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    grade: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Enrollment(EnrollmentInDB):
    pass