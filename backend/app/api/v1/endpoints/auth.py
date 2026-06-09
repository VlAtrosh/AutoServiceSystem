from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.dependencies import get_db, get_current_user
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserRole
from app.models.client import Client

router = APIRouter(tags=["Авторизация"], prefix="/auth")


@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    
    if await repo.exists_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if await repo.exists_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    user = await repo.create_user(user_data, hashed_password)
    
    # ========== АВТОМАТИЧЕСКОЕ СОЗДАНИЕ КЛИЕНТА ==========
    if user_data.role == UserRole.CLIENT:
        client = Client(
            id=str(uuid.uuid4()),
            user_id=user.id,
            discount=0,
            total_spent=0,
            total_orders=0,
        )
        db.add(client)
        await db.commit()
        await db.refresh(client)
    
    access_token = create_access_token(subject=user.username)
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    
    user = await repo.get_by_username(login_data.username)
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.username)
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить пользователя (только админ)"""
    # Проверяем, что текущий пользователь - админ
    if current_user.role != UserRole.DIRECTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await repo.delete(user_id)
    return None

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить пользователя по ID (доступно всем авторизованным)"""
    from app.repositories.user_repository import UserRepository
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user