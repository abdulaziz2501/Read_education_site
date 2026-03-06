import qrcode
import os
from datetime import date
from backend import models, database

# Ensure tables are created
models.Base.metadata.create_all(bind=database.engine)

def generate_sample_certificate():
    db = database.SessionLocal()
    
    cert_id = "RE-2025-001"
    
    # Check if exists
    existing = db.query(models.Certificate).filter(models.Certificate.certificate_id == cert_id).first()
    if not existing:
        new_cert = models.Certificate(
            student_name="Aziz Azizov",
            course_name="Full Stack Web Development",
            certificate_id=cert_id,
            issue_date=date(2025, 1, 15)
        )
        db.add(new_cert)
        db.commit()
        db.refresh(new_cert)
        print(f"Created certificate {cert_id} for {new_cert.student_name}")
    else:
        print(f"Certificate {cert_id} already exists.")
    
    db.close()

    # Generate QR Code
    url = f"https://readeducation.uz/certificate/{cert_id}"
    qr = qrcode.make(url)
    os.makedirs("static/images", exist_ok=True)
    qr_filename = "static/images/sample_qr.png"
    qr.save(qr_filename)
    print(f"Saved QR code to {qr_filename}")

if __name__ == "__main__":
    generate_sample_certificate()
