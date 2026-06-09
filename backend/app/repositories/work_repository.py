from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, or_
from typing import List, Optional
from app.models.work import Work


class WorkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ========== CREATE ==========
    async def create(self, work: Work) -> Work:
        """Создать работу"""
        self.db.add(work)
        await self.db.commit()
        await self.db.refresh(work)
        return work
    
    # ========== READ ==========
    async def get_by_id(self, work_id: str) -> Optional[Work]:
        """Получить работу по ID"""
        result = await self.db.execute(
            select(Work).where(Work.id == work_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_code(self, code: str) -> Optional[Work]:
        """Получить работу по коду"""
        result = await self.db.execute(
            select(Work).where(Work.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[Work]:
        """Получить работы по категории"""
        result = await self.db.execute(
            select(Work)
            .where(Work.category == category)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Work]:
        """Получить все работы с пагинацией"""
        result = await self.db.execute(
            select(Work)
            .order_by(Work.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Work]:
        """Поиск работ по названию или коду"""
        search_pattern = f"%{query}%"
        result = await self.db.execute(
            select(Work)
            .where(
                or_(
                    Work.name.ilike(search_pattern),
                    Work.code.ilike(search_pattern),
                    Work.category.ilike(search_pattern)
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_active(self, skip: int = 0, limit: int = 100) -> List[Work]:
        """Получить активные работы"""
        result = await self.db.execute(
            select(Work)
            .where(Work.is_active == 1)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    # ========== UPDATE ==========
    async def update(self, work: Work) -> Work:
        """Обновить работу"""
        await self.db.commit()
        await self.db.refresh(work)
        return work
    
    async def increment_times_performed(self, work_id: str) -> Optional[Work]:
        """Увеличить счётчик выполнения работы"""
        work = await self.get_by_id(work_id)
        if work:
            work.times_performed += 1
            await self.db.commit()
            await self.db.refresh(work)
        return work
    
    async def update_rating(self, work_id: str, new_rating: float) -> Optional[Work]:
        """Обновить средний рейтинг работы"""
        work = await self.get_by_id(work_id)
        if work:
            # Пересчёт среднего рейтинга
            work.average_rating = (work.average_rating * work.times_performed + new_rating) / (work.times_performed + 1)
            await self.db.commit()
            await self.db.refresh(work)
        return work
    
    # ========== DELETE ==========
    async def delete(self, work_id: str) -> bool:
        """Удалить работу"""
        result = await self.db.execute(
            delete(Work).where(Work.id == work_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def soft_delete(self, work_id: str) -> Optional[Work]:
        """Мягкое удаление (архивация)"""
        work = await self.get_by_id(work_id)
        if work:
            work.is_active = 0
            await self.db.commit()
            await self.db.refresh(work)
        return work
    
    # ========== STATISTICS ==========
    async def count_by_category(self, category: str) -> int:
        """Количество работ в категории"""
        result = await self.db.execute(
            select(func.count()).select_from(Work).where(Work.category == category)
        )
        return result.scalar() or 0
    
    async def count_all(self) -> int:
        """Общее количество работ"""
        result = await self.db.execute(
            select(func.count()).select_from(Work)
        )
        return result.scalar() or 0
    
    async def get_top_works(self, limit: int = 10) -> List[Work]:
        """Самые часто выполняемые работы"""
        result = await self.db.execute(
            select(Work)
            .order_by(Work.times_performed.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_price_range(self, min_price: float, max_price: float) -> List[Work]:
        """Работы в ценовом диапазоне"""
        result = await self.db.execute(
            select(Work)
            .where(Work.price_per_hour >= min_price)
            .where(Work.price_per_hour <= max_price)
        )
        return result.scalars().all()