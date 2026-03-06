from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    full_name: str
    role: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# --- Course Schemas ---
class CourseBase(BaseModel):
    name: str
    description: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int

    class Config:
        orm_mode = True

# --- Certificate Schemas ---
class CertificateBase(BaseModel):
    certificate_id: str
    issue_date: date

class CertificateCreate(CertificateBase):
    student_id: int
    course_id: int

class CertificateResponse(CertificateBase):
    id: int
    student: UserResponse
    course: CourseResponse
    created_at: datetime

    class Config:
        orm_mode = True

class CertificatePublic(BaseModel):
    student_name: str
    course_name: str
    certificate_id: str
    issue_date: date
