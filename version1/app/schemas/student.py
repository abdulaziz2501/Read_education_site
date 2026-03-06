"""
Student schemas
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date, datetime
from typing import Optional

class StudentBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    notes: Optional[str] = None

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class StudentInDB(StudentBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: str

    model_config = ConfigDict(from_attributes=True)

class Student(StudentInDB):
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"