"""
Certificate verification routes
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.certificate import CertificateService

router = APIRouter(tags=["verification"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/{certificate_id}", response_class=HTMLResponse)
async def verify_certificate_page(
        request: Request,
        certificate_id: str,
        db: AsyncSession = Depends(get_db)
):
    """Certificate verification page"""
    service = CertificateService(db)
    result = await service.verify_certificate(certificate_id)

    return templates.TemplateResponse(
        "verify.html",
        {
            "request": request,
            "certificate": result,
            "page_title": "Certificate Verification"
        }
    )


@router.get("/api/{certificate_id}")
async def verify_certificate_api(
        certificate_id: str,
        db: AsyncSession = Depends(get_db)
):
    """Certificate verification API endpoint"""
    service = CertificateService(db)
    result = await service.verify_certificate(certificate_id)
    return JSONResponse(content=result)