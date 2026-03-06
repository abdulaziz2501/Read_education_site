from fastapi import FastAPI, Depends, HTTPException, Request, Response, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os
from datetime import date
from typing import List

import models, schemas, database, auth_utils

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="READ EDUCATION API")

# Ensure static and frontend dirs exist
os.makedirs("static", exist_ok=True)
os.makedirs("frontend", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="frontend")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth_utils.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(models.User).filter(models.User.username == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

async def get_admin_user(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user

# Initial Admin Creation (Demo purposes)
@app.on_event("startup")
def create_initial_admin():
    db = database.SessionLocal()
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin:
        new_admin = models.User(
            username="admin",
            full_name="Administrator",
            hashed_password=auth_utils.get_password_hash("admin123"),
            role="admin"
        )
        db.add(new_admin)
        db.commit()
    db.close()

# --- Frontend Routes ---
@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/verify", response_class=HTMLResponse)
async def read_verify(request: Request):
    return templates.TemplateResponse("verify.html", {"request": request})

@app.get("/certificate/{certificate_id}", response_class=HTMLResponse)
async def read_certificate(request: Request, certificate_id: str):
    return templates.TemplateResponse("certificate.html", {"request": request, "certificate_id": certificate_id})

# --- Auth API ---
@app.post("/api/auth/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth_utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = auth_utils.create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=schemas.UserResponse)
async def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# --- Student API ---
@app.get("/api/student/certificates", response_model=List[schemas.CertificateResponse])
async def get_student_certificates(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Certificate).filter(models.Certificate.student_id == current_user.id).all()

# --- Admin API ---
@app.post("/api/admin/users", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, admin: models.User = Depends(get_admin_user), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = models.User(
        username=user.username,
        full_name=user.full_name,
        hashed_password=auth_utils.get_password_hash(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/api/admin/users", response_model=List[schemas.UserResponse])
async def list_users(admin: models.User = Depends(get_admin_user), db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.post("/api/admin/courses", response_model=schemas.CourseResponse)
async def create_course(course: schemas.CourseCreate, admin: models.User = Depends(get_admin_user), db: Session = Depends(get_db)):
    new_course = models.Course(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@app.get("/api/admin/courses", response_model=List[schemas.CourseResponse])
async def list_courses(admin: models.User = Depends(get_admin_user), db: Session = Depends(get_db)):
    return db.query(models.Course).all()

@app.post("/api/admin/issue-certificate", response_model=schemas.CertificateResponse)
async def issue_certificate(cert_data: schemas.CertificateCreate, admin: models.User = Depends(get_admin_user), db: Session = Depends(get_db)):
    # Check if user and course exist
    user = db.query(models.User).get(cert_data.student_id)
    course = db.query(models.Course).get(cert_data.course_id)
    if not user or not course:
        raise HTTPException(status_code=404, detail="User or Course not found")
    
    new_cert = models.Certificate(
        student_id=cert_data.student_id,
        course_id=cert_data.course_id,
        certificate_id=cert_data.certificate_id,
        issue_date=cert_data.issue_date
    )
    db.add(new_cert)
    db.commit()
    db.refresh(new_cert)
    return new_cert

# --- Public API ---
@app.get("/api/verify/{certificate_id}", response_model=schemas.CertificatePublic)
def verify_certificate(certificate_id: str, db: Session = Depends(get_db)):
    cert = db.query(models.Certificate).filter(models.Certificate.certificate_id == certificate_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate Not Found")
    
    return {
        "student_name": cert.student.full_name,
        "course_name": cert.course.name,
        "certificate_id": cert.certificate_id,
        "issue_date": cert.issue_date
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
