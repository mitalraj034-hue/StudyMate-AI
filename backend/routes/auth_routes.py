from datetime import timedelta
from typing import Optional
import re
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, User, ActivityLog
from auth import hash_password, verify_password, create_access_token, get_current_user
from config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

def validate_email_format(email: str) -> str:
    cleaned = email.strip().lower()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", cleaned):
        raise HTTPException(status_code=400, detail="Invalid email address format.")
    return cleaned


class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str
    confirm_password: Optional[str] = None
    major: Optional[str] = "Computer Science / General"
    target_exam: Optional[str] = "Semester Exams"


class LoginRequest(BaseModel):
    email: str
    password: str


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    major: Optional[str] = None
    target_exam: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    email: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    clean_email = validate_email_format(req.email)
    if req.confirm_password and req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")
    
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    existing_user = db.query(User).filter(User.email == clean_email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    new_user = User(
        email=clean_email,
        full_name=req.full_name.strip(),
        hashed_password=hash_password(req.password),
        major=req.major or "General Studies",
        target_exam=req.target_exam or "Semester Exams"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Log activity
    log = ActivityLog(
        user_id=new_user.id,
        activity_type="register",
        title="Account Created",
        description="Welcome to StudyMate AI! Start by uploading your study materials."
    )
    db.add(log)
    db.commit()

    token = create_access_token(data={"sub": str(new_user.id), "email": new_user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "major": new_user.major,
            "target_exam": new_user.target_exam
        }
    }


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    clean_email = validate_email_format(req.email)
    user = db.query(User).filter(User.email == clean_email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "major": user.major,
            "target_exam": user.target_exam
        }
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "major": current_user.major,
        "target_exam": current_user.target_exam,
        "created_at": current_user.created_at.isoformat()
    }


@router.put("/profile")
def update_profile(req: ProfileUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.full_name:
        current_user.full_name = req.full_name
    if req.major:
        current_user.major = req.major
    if req.target_exam:
        current_user.target_exam = req.target_exam

    if req.new_password:
        if not req.current_password or not verify_password(req.current_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password incorrect.")
        if len(req.new_password) < 6:
            raise HTTPException(status_code=400, detail="New password must be at least 6 characters.")
        current_user.hashed_password = hash_password(req.new_password)

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated successfully",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "major": current_user.major,
            "target_exam": current_user.target_exam
        }
    }


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    # Always return standard message to protect privacy
    return {
        "message": f"If an account exists for {req.email}, password reset instructions have been simulated and sent to your email."
    }
