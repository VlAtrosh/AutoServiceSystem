from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from typing import List, Optional

from app.models.car import Car


class CarRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ========== CREATE ==========
    async def create(self, car: Car) -> Car:
        """Добавить новый автомобиль"""
        self.db.add(car)
        await self.db.commit()
        await self.db.refresh(car)
        return car
    
    # ========== READ ==========
    async def get_by_id(self, car_id: str) -> Optional[Car]:
        """Получить автомобиль по ID"""
        result = await self.db.execute(
            select(Car).where(Car.id == car_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_license_plate(self, license_plate: str) -> Optional[Car]:
        """Получить автомобиль по госномеру"""
        result = await self.db.execute(
            select(Car).where(Car.license_plate == license_plate)
        )
        return result.scalar_one_or_none()
    
    async def get_by_vin(self, vin: str) -> Optional[Car]:
        """Получить автомобиль по VIN"""
        result = await self.db.execute(
            select(Car).where(Car.vin == vin)
        )
        return result.scalar_one_or_none()
    
    async def get_by_client_id(self, client_id: str, skip: int = 0, limit: int = 100) -> List[Car]:
        """Получить все автомобили клиента"""
        result = await self.db.execute(
            select(Car)
            .where(Car.client_id == client_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Car]:
        """Получить все автомобили с пагинацией"""
        result = await self.db.execute(
            select(Car).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def search(self, query: str) -> List[Car]:
        """Поиск автомобилей по госномеру, VIN, марке или модели"""
        search_pattern = f"%{query}%"
        result = await self.db.execute(
            select(Car).where(
                (Car.license_plate.ilike(search_pattern)) |
                (Car.vin.ilike(search_pattern)) |
                (Car.brand.ilike(search_pattern)) |
                (Car.model.ilike(search_pattern))
            )
        )
        return result.scalars().all()
    
    # ========== UPDATE ==========
    async def update(self, car: Car) -> Car:
        """Обновить данные автомобиля"""
        await self.db.commit()
        await self.db.refresh(car)
        return car
    
    # ========== DELETE ==========
    async def delete(self, car_id: str) -> bool:
        """Удалить автомобиль"""
        result = await self.db.execute(
            delete(Car).where(Car.id == car_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def delete_by_client_id(self, client_id: str) -> int:
        """Удалить все автомобили клиента"""
        result = await self.db.execute(
            delete(Car).where(Car.client_id == client_id)
        )
        await self.db.commit()
        return result.rowcount
    
    # ========== STATISTICS ==========
    async def count_by_client(self, client_id: str) -> int:
        """Количество автомобилей у клиента"""
        result = await self.db.execute(
            select(func.count()).select_from(Car).where(Car.client_id == client_id)
        )
        return result.scalar() or 0
    
    async def count_all(self) -> int:
        """Общее количество автомобилей"""
        result = await self.db.execute(
            select(func.count()).select_from(Car)
        )
        return result.scalar() or 0