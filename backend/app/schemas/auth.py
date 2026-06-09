from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    last_name: str = Field(..., min_length=1, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None
    role: UserRole = UserRole.CLIENT


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool = True
    full_name: Optional[str] = None
    
    @classmethod
    def from_orm(cls, user):
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            full_name=user.full_name if hasattr(user, 'full_name') else f"{user.last_name} {user.first_name}".strip()
        )
    
    class Config:
        from_attributes = True