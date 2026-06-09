# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r"^\+?7\d{10}$")
    email: EmailStr
    password: str = Field(..., min_length=3, max_length=100)
    role: UserRole = UserRole.CLIENT


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    full_name: Optional[str] = None
    phone: str
    email: str
    role: UserRole
    created_at: Optional[datetime] = None
    
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^\+?7\d{10}$")
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=3)
    
    class Config:
        from_attributes = True


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=3)