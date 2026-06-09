from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user
from app.schemas.auth import UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/user", tags=["user"])


@router.post("/register", response_model=UserResponse)
async def register(
    data: UserLogin,  # используй правильную схему
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    # TODO: реализовать регистрацию
    pass


@router.post("/login")
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    result = await auth_service.login(data.username, data.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return result


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return current_user