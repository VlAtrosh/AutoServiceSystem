from fastapi import APIRouter, Depends, HTTPException

from ...core.dependencies import get_current_user
from .schemas import UserLogin, UserRegister, UserResponse
from .service import UserService

router = APIRouter(prefix="/api/v1/user", tags=["user"])


@router.post("/register", response_model=UserResponse)
def register(data: UserRegister):
    user = UserService.register(
        name=data.name,
        phone=data.phone,
        email=data.email,
        password=data.password,
        role=data.role,
    )
    return UserResponse(
        id=user.id, name=user.name, phone=user.phone, email=user.email, role=user.role
    )


@router.post("/login")
def login(data: UserLogin):
    token = UserService.login(data.email, data.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        phone=current_user.phone,
        email=current_user.email,
        role=current_user.role,
    )
