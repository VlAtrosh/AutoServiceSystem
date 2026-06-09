from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User, UserRole
from app.models.mechanic import Mechanic, MechanicSpecialization, MechanicStatus
from app.schemas.mechanic import (
    MechanicCreate, MechanicResponse, MechanicUpdate,
    MechanicStatusUpdate, MechanicStatistics
)
from app.services.mechanic_service import MechanicService
from app.repositories.order_repository import OrderRepository
from app.repositories.mechanic_repository import MechanicRepository
from app.schemas.order import OrderResponse
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
import uuid

router = APIRouter(prefix="/mechanics", tags=["Механики"])


@router.get("/", response_model=List[MechanicResponse])
async def list_mechanics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    specialization: MechanicSpecialization = None,
    status: MechanicStatus = None
):
    """Получить список механиков"""
    repo = MechanicRepository(db)
    user_repo = UserRepository(db)
    
    if specialization:
        mechanics = await repo.get_by_specialization(specialization)
    elif status:
        if status == MechanicStatus.FREE:
            mechanics = await repo.get_free_mechanics()
        elif status == MechanicStatus.BUSY:
            mechanics = await repo.get_busy_mechanics()
        else:
            mechanics = await repo.get_all(skip, limit)
    else:
        mechanics = await repo.get_all(skip, limit)
    
    # Добавляем имя и фамилию
    result = []
    for mechanic in mechanics:
        user = await user_repo.get_by_id(mechanic.user_id)
        # Создаём словарь с данными механика + имя/фамилия
        mechanic_dict = {
            "id": mechanic.id,
            "user_id": mechanic.user_id,
            "first_name": user.first_name if user else None,
            "last_name": user.last_name if user else None,
            "specialization": mechanic.specialization,
            "experience_years": mechanic.experience_years,
            "education": mechanic.education,
            "certificates": mechanic.certificates,
            "status": mechanic.status,
            "rating": mechanic.rating,
            "completed_orders_count": mechanic.completed_orders_count,
            "total_hours_worked": mechanic.total_hours_worked,
            "total_earned": mechanic.total_earned,
            "schedule": mechanic.schedule,
            "phone": mechanic.phone,
            "email": mechanic.email,
            "created_at": mechanic.created_at,
            "updated_at": mechanic.updated_at
        }
        result.append(mechanic_dict)
    
    return result


@router.get("/free", response_model=List[MechanicResponse])
async def get_free_mechanics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить всех свободных механиков"""
    repo = MechanicRepository(db)
    return await repo.get_free_mechanics()


@router.get("/top", response_model=List[MechanicResponse])
async def get_top_mechanics(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить лучших механиков по рейтингу"""
    repo = MechanicRepository(db)
    return await repo.get_top_mechanics(limit)


@router.get("/{mechanic_id}", response_model=MechanicResponse)
async def get_mechanic(
    mechanic_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить механика по ID"""
    repo = MechanicRepository(db)
    mechanic = await repo.get_by_id(mechanic_id)
    
    if not mechanic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mechanic not found"
        )
    
    return mechanic


@router.get("/{mechanic_id}/statistics", response_model=MechanicStatistics)
async def get_mechanic_statistics(
    mechanic_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить статистику механика"""
    repo = MechanicRepository(db)
    mechanic = await repo.get_by_id(mechanic_id)
    
    if not mechanic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mechanic not found"
        )
    
    return {
        "completed_orders_count": mechanic.completed_orders_count,
        "total_hours_worked": mechanic.total_hours_worked,
        "total_earned": mechanic.total_earned,
        "rating": mechanic.rating
    }


@router.post("/", response_model=MechanicResponse, status_code=status.HTTP_201_CREATED)
async def create_mechanic(
    request: MechanicCreate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Создать механика (только админ)"""
    repo = MechanicRepository(db)
    
    # Проверяем, не существует ли уже
    existing = await repo.get_by_user_id(request.user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mechanic already exists for this user"
        )
    
    mechanic = Mechanic(
        id=str(uuid.uuid4()),
        user_id=request.user_id,
        specialization=request.specialization,
        experience_years=request.experience_years
    )
    
    return await repo.create(mechanic)


@router.patch("/{mechanic_id}/status", response_model=MechanicResponse)
async def update_mechanic_status(
    mechanic_id: str,
    request: MechanicStatusUpdate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Изменить статус механика (только админ)"""
    repo = MechanicRepository(db)
    mechanic = await repo.change_status(mechanic_id, request.status)
    
    if not mechanic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mechanic not found"
        )
    
    return mechanic


@router.patch("/{mechanic_id}", response_model=MechanicResponse)
async def update_mechanic(
    mechanic_id: str,
    request: MechanicUpdate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Обновить данные механика (только админ)"""
    repo = MechanicRepository(db)
    mechanic = await repo.get_by_id(mechanic_id)
    
    if not mechanic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mechanic not found"
        )
    
    if request.specialization:
        mechanic.specialization = request.specialization
    if request.experience_years is not None:
        mechanic.experience_years = request.experience_years
    if request.rating:
        mechanic.rating = request.rating
    
    return await repo.update(mechanic)

@router.patch("/{order_id}/assign-mechanic", response_model=OrderResponse)
async def assign_mechanic_to_order(
    order_id: str,
    mechanic_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Назначить механика на заказ (только приёмщик или директор)"""
    if current_user.role not in [UserRole.RECEIVER, UserRole.DIRECTOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough rights"
        )
    
    # Проверяем, существует ли механик
    mechanic_repo = MechanicRepository(db)
    mechanic = await mechanic_repo.get_by_id(mechanic_id)
    if not mechanic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mechanic not found"
        )
    
    # Проверяем, существует ли заказ
    order_repo = OrderRepository(db)
    order = await order_repo.get_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Назначаем механика
    order.mechanic_id = mechanic_id
    await order_repo.update(order)
    
    # Меняем статус механика на BUSY
    await mechanic_repo.change_status(mechanic_id, "busy")
    
    return order


@router.delete("/{mechanic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mechanic(
    mechanic_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Удалить механика (только админ)"""
    repo = MechanicRepository(db)
    deleted = await repo.delete(mechanic_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mechanic not found"
        )