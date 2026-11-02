import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.extra import ActivityLog
from app.schemas.user import UserCreate, UserLogin, UserProfileUpdate, ForgotPasswordRequest
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def validate_email_format(email: str) -> str:
    cleaned = email.strip().lower()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", cleaned):
        raise HTTPException(status_code=400, detail="Invalid email address format.")
    return cleaned


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(req: UserCreate, db: Session = Depends(get_db)):
    clean_email = validate_email_format(req.email)
    if req.confirm_password and req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    existing_user = db.query(User).filter(User.email == clean_email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    display_name = (req.name or req.full_name or clean_email.split("@")[0]).strip()

    new_user = User(
        name=display_name,
        email=clean_email,
        password_hash=hash_password(req.password),
        major=req.major or "General Studies",
        target_exam=req.target_exam or "Semester Exams"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

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
            "name": new_user.name,
            "full_name": new_user.name,
            "major": new_user.major,
            "target_exam": new_user.target_exam
        }
    }


@router.post("/login")
def login(req: UserLogin, db: Session = Depends(get_db)):
    clean_email = validate_email_format(req.email)
    user = db.query(User).filter(User.email == clean_email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "full_name": user.name,
            "major": user.major,
            "target_exam": user.target_exam
        }
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "full_name": current_user.name,
        "major": current_user.major,
        "target_exam": current_user.target_exam,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }


@router.put("/profile")
def update_profile(
    req: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if req.name:
        current_user.name = req.name.strip()
    elif req.full_name:
        current_user.name = req.full_name.strip()

    if req.major:
        current_user.major = req.major.strip()
    if req.target_exam:
        current_user.target_exam = req.target_exam.strip()

    if req.new_password:
        if not req.current_password or not verify_password(req.current_password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="Current password incorrect.")
        if len(req.new_password) < 6:
            raise HTTPException(status_code=400, detail="New password must be at least 6 characters.")
        current_user.password_hash = hash_password(req.new_password)

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated successfully.",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "full_name": current_user.name,
            "major": current_user.major,
            "target_exam": current_user.target_exam
        }
    }


@router.post("/forgot-password")
def forgot_password(
    req: Optional[ForgotPasswordRequest] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    target_email = ""
    if req and req.email:
        target_email = req.email
    elif email:
        target_email = email
    else:
        raise HTTPException(status_code=400, detail="Email is required.")

    clean_email = validate_email_format(target_email)
    user = db.query(User).filter(User.email == clean_email).first()
    return {
        "message": f"If an account is associated with {clean_email}, password reset instructions have been sent."
    }
