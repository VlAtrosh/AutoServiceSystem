from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.car_repository import CarRepository
from app.models.car import Car
import uuid


class CarService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.car_repo = CarRepository(db)
    
    async def get_all(self) -> list[Car]:
        """Получить все автомобили"""
        return await self.car_repo.get_all()
    
    async def get_by_id(self, car_id: str) -> Car | None:
        """Получить автомобиль по ID"""
        return await self.car_repo.get_by_id(car_id)
    
    async def get_by_client(self, client_id: str) -> list[Car]:
        """Получить автомобили клиента"""
        return await self.car_repo.get_by_client_id(client_id)
    
    async def create(self, client_id: str, car_data: dict) -> Car:
        """Создать автомобиль"""
        car = Car(
            id=str(uuid.uuid4())[:8],
            client_id=client_id,
            brand=car_data.get("brand"),
            model=car_data.get("model"),
            year=car_data.get("year"),
            license_plate=car_data.get("license_plate"),
            vin=car_data.get("vin"),
            color=car_data.get("color")
        )
        return await self.car_repo.create(car)
    
    async def update(self, car_id: str, car_data: dict) -> Car | None:
        """Обновить автомобиль"""
        car = await self.car_repo.get_by_id(car_id)
        if not car:
            return None
        
        if "brand" in car_data:
            car.brand = car_data["brand"]
        if "model" in car_data:
            car.model = car_data["model"]
        if "year" in car_data:
            car.year = car_data["year"]
        if "license_plate" in car_data:
            car.license_plate = car_data["license_plate"]
        if "vin" in car_data:
            car.vin = car_data["vin"]
        if "color" in car_data:
            car.color = car_data["color"]
        
        return await self.car_repo.update(car)
    
    async def delete(self, car_id: str) -> bool:
        """Удалить автомобиль"""
        return await self.car_repo.delete(car_id)