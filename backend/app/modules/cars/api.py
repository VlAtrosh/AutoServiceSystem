from fastapi import APIRouter, Depends, HTTPException

from ...core.dependencies import get_current_user
from ..user.models import User, UserRole
from .schemas import CarCreate, CarResponse, CarUpdate
from .service import CarService

router = APIRouter(prefix="/api/v1/cars", tags=["cars"])


@router.get("/", response_model=list[CarResponse])
def get_cars(current_user: User = Depends(get_current_user)):
    """Получить список автомобилей (все или только свои)"""
    if current_user.role == UserRole.CLIENT:
        cars = CarService.get_by_client(current_user.id)
    else:
        cars = CarService.get_all()
    return cars


@router.get("/{car_id}", response_model=CarResponse)
def get_car(car_id: str, current_user: User = Depends(get_current_user)):
    """Получить автомобиль по ID"""
    car = CarService.get_by_id(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    # Клиент может видеть только свои автомобили
    if current_user.role == UserRole.CLIENT and car.get("client_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return car


@router.post("/", response_model=CarResponse)
def create_car(car_data: CarCreate, current_user: User = Depends(get_current_user)):
    """Добавить новый автомобиль"""
    new_car = CarService.create(
        {
            "client_id": current_user.id,
            "brand": car_data.brand,
            "model": car_data.model,
            "year": car_data.year,
            "license_plate": car_data.license_plate,
            "vin": car_data.vin,
            "color": car_data.color,
        }
    )
    return new_car


@router.put("/{car_id}", response_model=CarResponse)
def update_car(
    car_id: str, car_data: CarUpdate, current_user: User = Depends(get_current_user)
):
    """Обновить автомобиль"""
    existing = CarService.get_by_id(car_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Car not found")

    # Проверка прав
    if (
        existing.get("client_id") != current_user.id
        and current_user.role != UserRole.DIRECTOR
    ):
        raise HTTPException(status_code=403, detail="Not enough rights")

    # Обновляем только переданные поля
    update_data = existing.copy()
    if car_data.brand is not None:
        update_data["brand"] = car_data.brand
    if car_data.model is not None:
        update_data["model"] = car_data.model
    if car_data.year is not None:
        update_data["year"] = car_data.year
    if car_data.license_plate is not None:
        update_data["license_plate"] = car_data.license_plate
    if car_data.vin is not None:
        update_data["vin"] = car_data.vin
    if car_data.color is not None:
        update_data["color"] = car_data.color

    updated = CarService.update(car_id, update_data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    return updated


@router.delete("/{car_id}")
def delete_car(car_id: str, current_user: User = Depends(get_current_user)):
    """Удалить автомобиль"""
    existing = CarService.get_by_id(car_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Car not found")

    if (
        existing.get("client_id") != current_user.id
        and current_user.role != UserRole.DIRECTOR
    ):
        raise HTTPException(status_code=403, detail="Not enough rights")

    if CarService.delete(car_id):
        return {"status": "ok", "message": "Car deleted"}
    raise HTTPException(status_code=500, detail="Delete failed")
