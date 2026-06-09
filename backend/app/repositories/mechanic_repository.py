# app/repositories/mechanic_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_
from typing import List, Optional

from app.models.mechanic import Mechanic, MechanicStatus, MechanicSpecialization


class MechanicRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ========== CREATE ==========
    async def create(self, mechanic: Mechanic) -> Mechanic:
        """Добавить нового механика"""
        self.db.add(mechanic)
        await self.db.commit()
        await self.db.refresh(mechanic)
        return mechanic
    
    # ========== READ ==========
    async def get_by_id(self, mechanic_id: str) -> Optional[Mechanic]:
        """Получить механика по ID"""
        result = await self.db.execute(
            select(Mechanic).where(Mechanic.id == mechanic_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: str) -> Optional[Mechanic]:
        """Получить механика по ID пользователя"""
        result = await self.db.execute(
            select(Mechanic).where(Mechanic.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Mechanic]:
        """Получить всех механиков с пагинацией"""
        result = await self.db.execute(
            select(Mechanic).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_specialization(self, specialization: MechanicSpecialization) -> List[Mechanic]:
        """Получить механиков по специализации"""
        result = await self.db.execute(
            select(Mechanic).where(Mechanic.specialization == specialization)
        )
        return result.scalars().all()
    
    async def get_free_mechanics(self) -> List[Mechanic]:
        """Получить всех свободных механиков"""
        result = await self.db.execute(
            select(Mechanic).where(Mechanic.status == MechanicStatus.FREE)
        )
        return result.scalars().all()
    
    async def get_available_mechanics(self) -> List[Mechanic]:
        """Получить доступных механиков (свободные и на перерыве)"""
        result = await self.db.execute(
            select(Mechanic).where(
                Mechanic.status.in_([MechanicStatus.FREE, MechanicStatus.ON_BREAK])
            )
        )
        return result.scalars().all()
    
    async def get_busy_mechanics(self) -> List[Mechanic]:
        """Получить занятых механиков"""
        result = await self.db.execute(
            select(Mechanic).where(Mechanic.status == MechanicStatus.BUSY)
        )
        return result.scalars().all()
    
    async def get_top_mechanics(self, limit: int = 10) -> List[Mechanic]:
        """Получить лучших механиков по рейтингу"""
        result = await self.db.execute(
            select(Mechanic)
            .order_by(Mechanic.rating.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_experience(self, min_years: float, max_years: float) -> List[Mechanic]:
        """Получить механиков с опытом в диапазоне"""
        result = await self.db.execute(
            select(Mechanic)
            .where(Mechanic.experience_years >= min_years)
            .where(Mechanic.experience_years <= max_years)
        )
        return result.scalars().all()
    
    # ========== UPDATE ==========
    async def update(self, mechanic: Mechanic) -> Mechanic:
        """Обновить данные механика"""
        await self.db.commit()
        await self.db.refresh(mechanic)
        return mechanic

    
    async def change_status(self, mechanic_id: str, new_status: str) -> Optional[Mechanic]:
        """Изменить статус механика"""
        mechanic = await self.get_by_id(mechanic_id)
        if mechanic:
            mechanic.status = new_status
            await self.db.commit()
            await self.db.refresh(mechanic)
        return mechanic


    async def increment_completed_orders(self, mechanic_id: str, hours: float, earned: float) -> Optional[Mechanic]:
        """Увеличить статистику механика после завершения заказа"""
        mechanic = await self.get_by_id(mechanic_id)
        if mechanic:
            mechanic.completed_orders_count += 1
            mechanic.total_hours_worked += hours
            mechanic.total_earned += earned
            mechanic.status = MechanicStatus.FREE
            await self.db.commit()
            await self.db.refresh(mechanic)
        return mechanic
    
    async def update_rating(self, mechanic_id: str, new_rating: float) -> Optional[Mechanic]:
        """Обновить рейтинг механика"""
        mechanic = await self.get_by_id(mechanic_id)
        if mechanic:
            mechanic.rating = new_rating
            await self.db.commit()
            await self.db.refresh(mechanic)
        return mechanic
    
    # ========== DELETE ==========
    async def delete(self, mechanic_id: str) -> bool:
        """Удалить механика"""
        result = await self.db.execute(
            delete(Mechanic).where(Mechanic.id == mechanic_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # ========== STATISTICS ==========
    async def count_by_status(self, status: MechanicStatus) -> int:
        """Количество механиков по статусу"""
        result = await self.db.execute(
            select(func.count()).select_from(Mechanic).where(Mechanic.status == status)
        )
        return result.scalar() or 0
    
    async def count_by_specialization(self, specialization: MechanicSpecialization) -> int:
        """Количество механиков по специализации"""
        result = await self.db.execute(
            select(func.count()).select_from(Mechanic).where(Mechanic.specialization == specialization)
        )
        return result.scalar() or 0
    
    async def count_free(self) -> int:
        """Количество свободных механиков"""
        return await self.count_by_status(MechanicStatus.FREE)
    
    async def count_busy(self) -> int:
        """Количество занятых механиков"""
        return await self.count_by_status(MechanicStatus.BUSY)
    
    async def get_average_rating(self) -> float:
        """Средний рейтинг всех механиков"""
        result = await self.db.execute(
            select(func.avg(Mechanic.rating))
        )
        return result.scalar() or 0.0
    
    async def get_total_hours_worked(self) -> float:
        """Общее количество отработанных часов"""
        result = await self.db.execute(
            select(func.sum(Mechanic.total_hours_worked))
        )
        return result.scalar() or 0.0
    
    async def get_total_earned(self) -> float:
        """Общая заработанная сумма"""
        result = await self.db.execute(
            select(func.sum(Mechanic.total_earned))
        )
        return result.scalar() or 0.0
    
    async def count_all(self) -> int:
        """Общее количество механиков"""
        result = await self.db.execute(
            select(func.count()).select_from(Mechanic)
        )
        return result.scalar() or 0