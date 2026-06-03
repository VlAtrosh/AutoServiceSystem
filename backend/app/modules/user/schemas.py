from pydantic import BaseModel

from .models import UserRole


class UserRegister(BaseModel):
    name: str
    phone: str
    email: str
    password: str
    role: UserRole = UserRole.CLIENT


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    phone: str
    email: str
    role: UserRole
