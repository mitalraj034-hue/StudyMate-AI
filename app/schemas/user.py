from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: str
    name: str
    major: Optional[str] = "General Studies"
    target_exam: Optional[str] = "Semester Exams"


class UserCreate(BaseModel):
    name: Optional[str] = None
    full_name: Optional[str] = None
    email: str
    password: str
    confirm_password: Optional[str] = None
    major: Optional[str] = "General Studies"
    target_exam: Optional[str] = "Semester Exams"


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    major: Optional[str] = None
    target_exam: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ForgotPasswordRequest(BaseModel):
    email: str


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    full_name: Optional[str] = None
    major: Optional[str] = None
    target_exam: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None
