from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, or_
from typing import List, Optional
from app.models.part import Part


class PartRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ========== CREATE ==========
    async def create(self, part: Part) -> Part:
        """Создать запчасть"""
        self.db.add(part)
        await self.db.commit()
        await self.db.refresh(part)
        return part
    
    # ========== READ ==========
    async def get_by_id(self, part_id: str) -> Optional[Part]:
        """Получить запчасть по ID"""
        result = await self.db.execute(
            select(Part).where(Part.id == part_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_code(self, code: str) -> Optional[Part]:
        """Получить запчасть по коду"""
        result = await self.db.execute(
            select(Part).where(Part.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_by_article(self, article: str) -> Optional[Part]:
        """Получить запчасть по артикулу"""
        result = await self.db.execute(
            select(Part).where(Part.article == article)
        )
        return result.scalar_one_or_none()
    
    async def get_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[Part]:
        """Получить запчасти по категории"""
        result = await self.db.execute(
            select(Part)
            .where(Part.category == category)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_brand(self, brand: str, skip: int = 0, limit: int = 100) -> List[Part]:
        """Получить запчасти по бренду"""
        result = await self.db.execute(
            select(Part)
            .where(Part.brand == brand)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_in_stock(self, skip: int = 0, limit: int = 100) -> List[Part]:
        """Получить запчасти в наличии (quantity > 0)"""
        result = await self.db.execute(
            select(Part)
            .where(Part.quantity > 0)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_low_stock(self, threshold: int = 5) -> List[Part]:
        """Получить запчасти с низким остатком"""
        result = await self.db.execute(
            select(Part)
            .where(Part.quantity <= threshold)
            .where(Part.quantity > 0)
        )
        return result.scalars().all()
    
    async def get_out_of_stock(self) -> List[Part]:
        """Получить запчасти с нулевым остатком"""
        result = await self.db.execute(
            select(Part)
            .where(Part.quantity == 0)
        )
        return result.scalars().all()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Part]:
        """Получить все запчасти с пагинацией"""
        result = await self.db.execute(
            select(Part)
            .order_by(Part.name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Part]:
        """Поиск запчастей по названию, артикулу или коду"""
        search_pattern = f"%{query}%"
        result = await self.db.execute(
            select(Part)
            .where(
                or_(
                    Part.name.ilike(search_pattern),
                    Part.article.ilike(search_pattern),
                    Part.code.ilike(search_pattern),
                    Part.brand.ilike(search_pattern)
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_active(self, skip: int = 0, limit: int = 100) -> List[Part]:
        """Получить активные запчасти"""
        result = await self.db.execute(
            select(Part)
            .where(Part.is_active == 1)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    # ========== UPDATE ==========
    async def update(self, part: Part) -> Part:
        """Обновить запчасть"""
        await self.db.commit()
        await self.db.refresh(part)
        return part
    
    async def update_quantity(self, part_id: str, delta: int) -> Optional[Part]:
        """Изменить количество на складе"""
        part = await self.get_by_id(part_id)
        if part:
            part.quantity += delta
            await self.db.commit()
            await self.db.refresh(part)
        return part
    
    async def reserve(self, part_id: str, quantity: int) -> bool:
        """Зарезервировать запчасть"""
        part = await self.get_by_id(part_id)
        if part and part.quantity >= quantity:
            part.quantity -= quantity
            part.reserved += quantity
            await self.db.commit()
            return True
        return False
    
    async def unreserve(self, part_id: str, quantity: int) -> bool:
        """Отменить резервирование"""
        part = await self.get_by_id(part_id)
        if part and part.reserved >= quantity:
            part.quantity += quantity
            part.reserved -= quantity
            await self.db.commit()
            return True
        return False
    
    # ========== DELETE ==========
    async def delete(self, part_id: str) -> bool:
        """Удалить запчасть"""
        result = await self.db.execute(
            delete(Part).where(Part.id == part_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def soft_delete(self, part_id: str) -> Optional[Part]:
        """Мягкое удаление (архивация)"""
        part = await self.get_by_id(part_id)
        if part:
            part.is_active = 0
            await self.db.commit()
            await self.db.refresh(part)
        return part
    
    # ========== STATISTICS ==========
    async def count_by_category(self, category: str) -> int:
        """Количество запчастей в категории"""
        result = await self.db.execute(
            select(func.count()).select_from(Part).where(Part.category == category)
        )
        return result.scalar() or 0
    
    async def count_all(self) -> int:
        """Общее количество запчастей"""
        result = await self.db.execute(
            select(func.count()).select_from(Part)
        )
        return result.scalar() or 0
    
    async def get_total_stock_value(self) -> float:
        """Общая стоимость остатков"""
        result = await self.db.execute(
            select(func.sum(Part.quantity * Part.price))
        )
        return result.scalar() or 0.0