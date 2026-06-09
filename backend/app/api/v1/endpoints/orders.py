from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.schemas.order import (
    OrderCreate, OrderResponse, OrderItemAdd,
    OrderStatusUpdate, OrderListResponse
)
from app.services.order_service import OrderService
from app.repositories.order_repository import OrderRepository
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.car_repository import CarRepository
from app.repositories.mechanic_repository import MechanicRepository
from app.repositories.work_repository import WorkRepository
from app.schemas.order import OrderStatusResponse



router = APIRouter(prefix="/orders", tags=["Заказы"])


@router.get("/", response_model=List[OrderListResponse])
async def list_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Получить список заказов"""
    order_repo = OrderRepository(db)
    
    if current_user.role == UserRole.CLIENT:
        orders = await order_repo.get_by_client_id(current_user.id, skip, limit)
    else:
        orders = await order_repo.get_all(skip, limit)
    
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить заказ по ID"""
    order_repo = OrderRepository(db)
    order = await order_repo.get_by_id(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if current_user.role == UserRole.CLIENT and order.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    from app.repositories.order_item_repository import OrderItemRepository
    item_repo = OrderItemRepository(db)
    items = await item_repo.get_by_order_id(order_id)
    
    result = {
        "id": order.id,
        "number": order.number,
        "client_id": order.client_id,
        "car_info": order.car_info,
        "status": order.status,
        "total": order.total,
        "mechanic_id": order.mechanic_id,
        "created_at": order.created_at,
        "completed_at": order.completed_at,
        "items": items
    }
    
    return result


@router.post("/", response_model=OrderStatusResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать новый заказ"""
    if current_user.role not in [UserRole.CLIENT, UserRole.RECEIVER, UserRole.DIRECTOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough rights"
        )
    
    order_service = OrderService(db)
    
    car_repo = CarRepository(db)
    car = await car_repo.get_by_id(request.car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    if car.client_id != current_user.id and current_user.role not in [UserRole.RECEIVER, UserRole.DIRECTOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create orders for your own cars"
        )
    
    from app.repositories.client_repository import ClientRepository
    client_repo = ClientRepository(db)
    client = await client_repo.get_by_user_id(car.client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found for this car owner"
        )

    order = await order_service.create_order(
        client_id=client.id,
        car_id=request.car_id,
        car_info=f"{car.brand} {car.model} {car.year}"
    )
    
    return order


@router.post("/{order_id}/add-work", response_model=OrderStatusResponse)
async def add_work_to_order(
    order_id: str,
    work_id: str,
    hours: float = 1.0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Добавить работу в заказ (только механик или админ)"""
    if current_user.role not in [UserRole.MECHANIC, UserRole.DIRECTOR, UserRole.RECEIVER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mechanic or admin can add works"
        )
    
    order_service = OrderService(db)
    
    work_repo = WorkRepository(db)
    work = await work_repo.get_by_id(work_id)
    if not work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found"
        )
    
    order = await order_service.add_work(order_id, work_id, hours, work.name, work.price_per_hour)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.patch("/{order_id}/assign-mechanic", response_model=OrderStatusResponse)
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
    
    mechanic_repo = MechanicRepository(db)
    mechanic = await mechanic_repo.get_by_id(mechanic_id)
    if not mechanic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mechanic not found"
        )
    
    order_repo = OrderRepository(db)
    order = await order_repo.get_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order.mechanic_id = mechanic_id
    await order_repo.update(order)
    
    await mechanic_repo.change_status(mechanic_id, "busy")
    
    return order


@router.patch("/{order_id}/status", response_model=OrderStatusResponse)
async def update_order_status(
    order_id: str,
    request: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Изменить статус заказа"""
    if current_user.role not in [UserRole.MECHANIC, UserRole.RECEIVER, UserRole.DIRECTOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough rights"
        )
    
    order_service = OrderService(db)
    order = await order_service.change_status(order_id, request.new_status, current_user.role)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change status or order not found"
        )
    
    return order
