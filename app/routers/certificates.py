"""
Certificate management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.models.certificate import Certificate
from app.schemas.certificate import Certificate as CertificateSchema, CertificateCreate
from app.services.certificate import CertificateService

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.get("/", response_model=List[CertificateSchema])
async def get_certificates(
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
):
    """Get all certificates"""
    result = await db.execute(
        select(Certificate)
        .offset(skip)
        .limit(limit)
        .order_by(Certificate.issue_date.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=CertificateSchema, status_code=status.HTTP_201_CREATED)
async def create_certificate(
        certificate_data: CertificateCreate,
        background_tasks: BackgroundTasks,
        current_user: User = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
):
    """Create a new certificate"""
    service = CertificateService(db)

    # Set issued_by to current user
    certificate_data.issued_by = str(current_user.id)

    certificate = await service.create_certificate(certificate_data)
    return certificate


@router.get("/{certificate_id}/download")
async def download_certificate(
        certificate_id: str,
        current_user: User = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
):
    """Download certificate PDF"""
    result = await db.execute(
        select(Certificate).where(Certificate.id == certificate_id)
    )
    certificate = result.scalar_one_or_none()

    if not certificate or not certificate.pdf_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate or PDF not found"
        )

    if not os.path.exists(certificate.pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found"
        )

    return FileResponse(
        certificate.pdf_path,
        media_type="application/pdf",
        filename=f"certificate_{certificate.certificate_id}.pdf"
    )


@router.post("/{certificate_id}/invalidate")
async def invalidate_certificate(
        certificate_id: str,
        current_user: User = Depends(get_current_admin_user),
        db: AsyncSession = Depends(get_db)
):
    """Invalidate a certificate"""
    result = await db.execute(
        select(Certificate).where(Certificate.id == certificate_id)
    )
    certificate = result.scalar_one_or_none()

    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )

    certificate.is_valid = False
    await db.commit()

    return {"message": "Certificate invalidated successfully"}