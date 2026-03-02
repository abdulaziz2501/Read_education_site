"""
Certificate schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class CertificateBase(BaseModel):
    student_id: str
    course_id: str
    enrollment_id: str
    grade: Optional[str] = None
    expiry_date: Optional[datetime] = None

class CertificateCreate(CertificateBase):
    issued_by: str

class CertificateInDB(CertificateBase):
    id: str
    certificate_id: str
    issue_date: datetime
    qr_code: Optional[str] = None
    pdf_path: Optional[str] = None
    is_valid: bool
    issued_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Certificate(CertificateInDB):
    pass

class CertificateVerify(BaseModel):
    certificate_id: str
    student_name: str
    course_name: str
    issue_date: datetime
    expiry_date: Optional[datetime] = None
    is_valid: bool
    grade: Optional[str] = None