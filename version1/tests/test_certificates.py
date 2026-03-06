"""
Tests for certificate functionality
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.student import Student
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.certificate import Certificate
from app.services.certificate import CertificateService


@pytest.mark.asyncio
async def test_generate_certificate_id(client: AsyncClient, db: AsyncSession):
    """Test certificate ID generation"""
    service = CertificateService(db)
    cert_id = await service.generate_certificate_id()

    assert cert_id is not None
    assert len(cert_id) > 0
    assert isinstance(cert_id, str)


@pytest.mark.asyncio
async def test_create_certificate(
        client: AsyncClient,
        db: AsyncSession,
        test_student: Student,
        test_course: Course,
        test_enrollment: Enrollment,
        admin_token: str
):
    """Test certificate creation"""
    service = CertificateService(db)

    certificate_data = {
        "student_id": test_student.id,
        "course_id": test_course.id,
        "enrollment_id": test_enrollment.id,
        "grade": "A",
        "issued_by": "admin-id"
    }

    certificate = await service.create_certificate(certificate_data)

    assert certificate is not None
    assert certificate.student_id == test_student.id
    assert certificate.course_id == test_course.id
    assert certificate.grade == "A"
    assert certificate.is_valid == True
    assert certificate.qr_code is not None
    assert certificate.pdf_path is not None


@pytest.mark.asyncio
async def test_verify_valid_certificate(
        client: AsyncClient,
        db: AsyncSession,
        test_certificate: Certificate
):
    """Test certificate verification - valid"""
    service = CertificateService(db)
    result = await service.verify_certificate(test_certificate.certificate_id)

    assert result["is_valid"] == True
    assert result["certificate_id"] == test_certificate.certificate_id
    assert "student_name" in result
    assert "course_name" in result


@pytest.mark.asyncio
async def test_verify_invalid_certificate(client: AsyncClient, db: AsyncSession):
    """Test certificate verification - invalid"""
    service = CertificateService(db)
    result = await service.verify_certificate("invalid-cert-id")

    assert result["is_valid"] == False
    assert result["message"] == "Certificate not found"


@pytest.mark.asyncio
async def test_certificate_api_endpoint(
        client: AsyncClient,
        test_certificate: Certificate
):
    """Test certificate API endpoint"""
    response = await client.get(f"/verify/api/{test_certificate.certificate_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] == True
    assert data["certificate_id"] == test_certificate.certificate_id


@pytest.mark.asyncio
async def test_certificate_verification_page(
        client: AsyncClient,
        test_certificate: Certificate
):
    """Test certificate verification page"""
    response = await client.get(f"/verify/{test_certificate.certificate_id}")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]