from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.dependencies import get_current_user, get_db
from app.models.user import User, UserRole
from app.models.car import Car
from app.schemas.car import CarCreate, CarUpdate, CarResponse
from app.repositories.car_repository import CarRepository

router = APIRouter(prefix="/cars", tags=["Автомобили"])


@router.get("/", response_model=List[CarResponse])
async def get_user_cars(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    repo = CarRepository(db)
    return await repo.get_by_client_id(current_user.id, skip, limit)


@router.get("/all", response_model=List[CarResponse])
async def get_all_cars(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    if current_user.role not in [UserRole.DIRECTOR, UserRole.RECEIVER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    repo = CarRepository(db)
    return await repo.get_all(skip, limit)


@router.get("/{car_id}", response_model=CarResponse)
async def get_car(
    car_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CarRepository(db)
    car = await repo.get_by_id(car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    if car.client_id != current_user.id and current_user.role not in [UserRole.DIRECTOR, UserRole.RECEIVER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return car


@router.post("/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
async def create_car(
    car_data: CarCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CarRepository(db)
    
    existing = await repo.get_by_license_plate(car_data.license_plate)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="License plate already exists"
        )
    
    car = Car(
        id=str(uuid.uuid4()),
        client_id=current_user.id,
        brand=car_data.brand,
        model=car_data.model,
        year=car_data.year,
        license_plate=car_data.license_plate,
        vin=car_data.vin,
        color=car_data.color
    )
    return await repo.create(car)


@router.patch("/{car_id}", response_model=CarResponse)
async def update_car(
    car_id: str,
    car_data: CarUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CarRepository(db)
    car = await repo.get_by_id(car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    if car.client_id != current_user.id and current_user.role not in [UserRole.DIRECTOR, UserRole.RECEIVER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    update_data = car_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(car, field, value)
    
    return await repo.update(car)


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(
    car_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CarRepository(db)
    car = await repo.get_by_id(car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    if car.client_id != current_user.id and current_user.role not in [UserRole.DIRECTOR, UserRole.RECEIVER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    await repo.delete(car_id)