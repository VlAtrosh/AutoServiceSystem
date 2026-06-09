from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User, UserRole
from app.models.client import Client
from app.schemas.client import (
    ClientCreate, ClientResponse, ClientUpdate,
)
from app.services.client_service import ClientService
from app.repositories.client_repository import ClientRepository
from app.repositories.order_repository import OrderRepository
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/clients", tags=["Клиенты"])


@router.get("/", response_model=List[ClientResponse])
async def list_clients(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: str = None,
):
    repo = ClientRepository(db)
    user_repo = UserRepository(db)
    
    if status:
        clients = await repo.get_by_status(status)
    else:
        clients = await repo.get_all(skip, limit)
    
    result = []
    for client in clients:
        user = await user_repo.get_by_id(client.user_id)
        result.append({
            "id": client.id,
            "user_id": client.user_id,
            "discount": client.discount,
            "total_spent": client.total_spent,
            "total_orders": client.total_orders,
            "last_visit": client.last_visit,
            "status": client.status,
            "created_at": client.created_at,
            "username": user.username if user else None,
            "email": user.email if user else None,
            "first_name": user.first_name if user else None,
            "last_name": user.last_name if user else None,
            "phone": user.phone if user else None,
            "role": user.role if user else None
        })
    
    return result


@router.get("/me", response_model=ClientResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить профиль текущего клиента"""
    repo = ClientRepository(db)
    client = await repo.get_by_user_id(current_user.id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found"
        )
    
    return client


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Получить клиента по ID (только админ)"""
    repo = ClientRepository(db)
    user_repo = UserRepository(db)
    
    client = await repo.get_by_id(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    user = await user_repo.get_by_id(client.user_id)
    
    return {
        "id": client.id,
        "user_id": client.user_id,
        "discount": client.discount,
        "total_spent": client.total_spent,
        "total_orders": client.total_orders,
        "last_visit": client.last_visit,
        "status": client.status,
        "created_at": client.created_at,
        "username": user.username if user else None,
        "email": user.email if user else None,
        "first_name": user.first_name if user else None,
        "last_name": user.last_name if user else None,
        "phone": user.phone if user else None,
        "role": user.role if user else None
    }

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    request: ClientCreate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Создать клиента (только админ)"""
    repo = ClientRepository(db)
    
    # Проверяем, не существует ли уже
    existing = await repo.get_by_user_id(request.user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client already exists for this user"
        )
    
    # Убираем id отсюда - он создастся автоматически
    client = Client(
        user_id=request.user_id,
        discount=request.discount or 0,
        preferred_contact=request.preferred_contact or "phone",
        receive_notifications=request.receive_notifications
    )
    
    return await repo.create(client)


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    request: ClientUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновить данные клиента"""
    repo = ClientRepository(db)
    client = await repo.get_by_id(client_id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Проверка доступа
    if current_user.role != UserRole.DIRECTOR:
        current_client = await repo.get_by_user_id(current_user.id)
        if not current_client or current_client.id != client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    if request.discount is not None:
        client.discount = request.discount
    if request.status:
        client.status = request.status
    if request.preferred_contact:
        client.preferred_contact = request.preferred_contact
    if request.receive_notifications is not None:
        client.receive_notifications = request.receive_notifications
    
    return await repo.update(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Удалить клиента (только админ)"""
    repo = ClientRepository(db)
    deleted = await repo.delete(client_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )