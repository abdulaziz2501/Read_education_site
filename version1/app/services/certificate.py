"""
Certificate generation service
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import qrcode
import base64
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.units import inch
import os

from app.models.certificate import Certificate
from app.models.student import Student
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.schemas.certificate import CertificateCreate
from app.core.config import settings


class CertificateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_certificate_id(self) -> str:
        """Generate a unique certificate ID"""
        while True:
            cert_id = secrets.token_urlsafe(16)
            # Check if exists
            result = await self.db.execute(
                select(Certificate).where(Certificate.certificate_id == cert_id)
            )
            if not result.scalar_one_or_none():
                return cert_id

    async def generate_qr_code(self, certificate_id: str) -> str:
        """Generate QR code for certificate verification"""
        verification_url = f"{settings.BASE_URL}/verify/{certificate_id}"

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )
        qr.add_data(verification_url)
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64 for storage
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return img_str

    async def generate_pdf_certificate(
            self,
            student: Student,
            course: Course,
            certificate: Certificate
    ) -> str:
        """Generate PDF certificate"""
        # Create certificates directory if not exists
        cert_dir = "certificates"
        os.makedirs(cert_dir, exist_ok=True)

        # PDF filename
        filename = f"{cert_dir}/{certificate.certificate_id}.pdf"

        # Create PDF
        c = canvas.Canvas(filename, pagesize=landscape(A4))
        width, height = landscape(A4)

        # Add border
        c.setStrokeColor(colors.HexColor("#2c3e50"))
        c.setLineWidth(5)
        c.rect(20, 20, width - 40, height - 40)

        # Add school name
        c.setFont("Helvetica-Bold", 36)
        c.setFillColor(colors.HexColor("#2c3e50"))
        c.drawCentredString(width / 2, height - 100, "School of Excellence")

        # Add certificate title
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(colors.HexColor("#3498db"))
        c.drawCentredString(width / 2, height - 180, "CERTIFICATE OF COMPLETION")

        # Add "This is to certify that"
        c.setFont("Helvetica", 16)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2, height - 250, "This is to certify that")

        # Add student name
        c.setFont("Helvetica-Bold", 32)
        c.setFillColor(colors.HexColor("#2c3e50"))
        c.drawCentredString(width / 2, height - 320, student.full_name)

        # Add course completion text
        c.setFont("Helvetica", 16)
        c.drawCentredString(width / 2, height - 370, f"has successfully completed the course")

        # Add course name
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(colors.HexColor("#3498db"))
        c.drawCentredString(width / 2, height - 420, course.title)

        # Add details
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.gray)
        c.drawCentredString(width / 2, height - 470,
                            f"Duration: {course.duration_weeks} weeks | Grade: {certificate.grade or 'Pass'}")

        # Add date
        c.drawCentredString(width / 2, height - 520, f"Issued on: {certificate.issue_date.strftime('%B %d, %Y')}")

        # Add certificate ID
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.gray)
        c.drawCentredString(width / 2, 50, f"Certificate ID: {certificate.certificate_id}")

        # Add QR code if available
        if certificate.qr_code:
            try:
                # Decode base64 QR code
                img_data = base64.b64decode(certificate.qr_code)
                img_buffer = BytesIO(img_data)
                c.drawImage(img_buffer, width - 150, 50, width=100, height=100)
            except:
                pass

        # Save PDF
        c.save()

        return filename

    async def create_certificate(self, certificate_data: CertificateCreate) -> Certificate:
        """Create a new certificate"""
        # Check if certificate already exists for this enrollment
        result = await self.db.execute(
            select(Certificate).where(Certificate.enrollment_id == certificate_data.enrollment_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Certificate already exists for this enrollment"
            )

        # Get student and course for PDF generation
        student_result = await self.db.execute(
            select(Student).where(Student.id == certificate_data.student_id)
        )
        student = student_result.scalar_one_or_none()

        course_result = await self.db.execute(
            select(Course).where(Course.id == certificate_data.course_id)
        )
        course = course_result.scalar_one_or_none()

        if not student or not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student or course not found"
            )

        # Generate certificate ID
        cert_id = await self.generate_certificate_id()

        # Generate QR code
        qr_code = await self.generate_qr_code(cert_id)

        # Create certificate
        certificate = Certificate(
            certificate_id=cert_id,
            student_id=certificate_data.student_id,
            course_id=certificate_data.course_id,
            enrollment_id=certificate_data.enrollment_id,
            grade=certificate_data.grade,
            expiry_date=certificate_data.expiry_date,
            qr_code=qr_code,
            issued_by=certificate_data.issued_by,
            is_valid=True
        )

        self.db.add(certificate)
        await self.db.commit()
        await self.db.refresh(certificate)

        # Generate PDF
        pdf_path = await self.generate_pdf_certificate(student, course, certificate)

        # Update certificate with PDF path
        certificate.pdf_path = pdf_path
        await self.db.commit()
        await self.db.refresh(certificate)

        return certificate

    async def verify_certificate(self, certificate_id: str) -> dict:
        """Verify a certificate by ID"""
        result = await self.db.execute(
            select(Certificate).where(Certificate.certificate_id == certificate_id)
        )
        certificate = result.scalar_one_or_none()

        if not certificate:
            return {
                "is_valid": False,
                "message": "Certificate not found"
            }

        # Check if certificate is valid
        if not certificate.is_valid:
            return {
                "is_valid": False,
                "message": "Certificate has been invalidated"
            }

        # Check expiry if set
        if certificate.expiry_date and certificate.expiry_date < datetime.utcnow():
            return {
                "is_valid": False,
                "message": "Certificate has expired"
            }

        # Get student and course info
        student_result = await self.db.execute(
            select(Student).where(Student.id == certificate.student_id)
        )
        student = student_result.scalar_one_or_none()

        course_result = await self.db.execute(
            select(Course).where(Course.id == certificate.course_id)
        )
        course = course_result.scalar_one_or_none()

        return {
            "is_valid": True,
            "certificate_id": certificate.certificate_id,
            "student_name": student.full_name if student else "Unknown",
            "course_name": course.title if course else "Unknown",
            "issue_date": certificate.issue_date,
            "expiry_date": certificate.expiry_date,
            "grade": certificate.grade,
            "message": "Certificate is valid"
        }