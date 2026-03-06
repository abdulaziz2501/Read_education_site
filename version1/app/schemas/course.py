"""
Course schemas
"""
from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from datetime import datetime
from typing import Optional, List, Dict, Any

class CourseBase(BaseModel):
    title: str
    slug: str
    description: str
    short_description: Optional[str] = None
    category: str
    duration_weeks: int = Field(..., gt=0)
    hours_per_week: float = Field(..., gt=0)
    price: float = Field(..., ge=0)
    curriculum: Optional[List[Dict[str, Any]]] = None
    requirements: Optional[List[str]] = None
    target_audience: Optional[str] = None
    max_students: Optional[int] = Field(None, gt=0)
    is_active: bool = True
    is_featured: bool = False
    thumbnail: Optional[HttpUrl] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    category: Optional[str] = None
    duration_weeks: Optional[int] = Field(None, gt=0)
    hours_per_week: Optional[float] = Field(None, gt=0)
    price: Optional[float] = Field(None, ge=0)
    curriculum: Optional[List[Dict[str, Any]]] = None
    requirements: Optional[List[str]] = None
    target_audience: Optional[str] = None
    max_students: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    thumbnail: Optional[HttpUrl] = None

class CourseInDB(CourseBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Course(CourseInDB):
    pass