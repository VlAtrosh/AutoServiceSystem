# app/repositories/order_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from typing import List, Optional
from datetime import datetime

from app.models.order import Order, OrderStatus, OrderItem


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ========== CREATE ==========
    async def create(self, order: Order) -> Order:
        """Создать новый заказ"""
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order
    
    async def add_item(self, order_id: str, item: OrderItem) -> OrderItem:
        """Добавить позицию (работу/запчасть) в заказ"""
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        
        # Обновляем сумму заказа
        await self._recalculate_total(order_id)
        return item
    
    # ========== READ ==========
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        """Получить заказ по ID"""
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_number(self, number: str) -> Optional[Order]:
        """Получить заказ по номеру"""
        result = await self.db.execute(
            select(Order).where(Order.number == number)
        )
        return result.scalar_one_or_none()
    
    async def get_by_client_id(self, client_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """Получить все заказы клиента"""
        result = await self.db.execute(
            select(Order)
            .where(Order.client_id == client_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_mechanic_id(self, mechanic_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """Получить заказы механика"""
        result = await self.db.execute(
            select(Order)
            .where(Order.mechanic_id == mechanic_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_status(self, status: OrderStatus, skip: int = 0, limit: int = 100) -> List[Order]:
        """Получить заказы по статусу"""
        result = await self.db.execute(
            select(Order)
            .where(Order.status == status)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """Получить все заказы с пагинацией"""
        result = await self.db.execute(
            select(Order)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Order]:
        """Получить заказы за период"""
        result = await self.db.execute(
            select(Order)
            .where(Order.created_at >= start_date)
            .where(Order.created_at <= end_date)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_order_items(self, order_id: str) -> List[OrderItem]:
        """Получить все позиции заказа"""
        result = await self.db.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        return result.scalars().all()
    
    # ========== UPDATE ==========
    async def update(self, order: Order) -> Order:
        """Обновить заказ"""
        await self.db.commit()
        await self.db.refresh(order)
        return order
    
    async def update_status(self, order_id: str, new_status: OrderStatus) -> Optional[Order]:
        """Обновить статус заказа"""
        order = await self.get_by_id(order_id)
        if order:
            order.status = new_status
            if new_status == OrderStatus.COMPLETED:
                order.completed_at = datetime.now()
            await self.db.commit()
            await self.db.refresh(order)
        return order
    
    async def assign_mechanic(self, order_id: str, mechanic_id: str) -> Optional[Order]:
        """Назначить механика на заказ"""
        order = await self.get_by_id(order_id)
        if order:
            order.mechanic_id = mechanic_id
            await self.db.commit()
            await self.db.refresh(order)
        return order
    
    async def _recalculate_total(self, order_id: str) -> None:
        """Пересчитать итоговую сумму заказа"""
        items = await self.get_order_items(order_id)
        total = sum(item.total for item in items)
        
        await self.db.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(total=total)
        )
        await self.db.commit()
    
    # ========== DELETE ==========
    async def delete(self, order_id: str) -> bool:
        """Удалить заказ"""
        result = await self.db.execute(
            delete(Order).where(Order.id == order_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def delete_item(self, item_id: str) -> bool:
        """Удалить позицию из заказа"""
        # Сначала получим order_id
        result = await self.db.execute(
            select(OrderItem).where(OrderItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            return False
        
        order_id = item.order_id
        
        # Удаляем позицию
        await self.db.execute(
            delete(OrderItem).where(OrderItem.id == item_id)
        )
        await self.db.commit()
        
        # Пересчитываем сумму
        await self._recalculate_total(order_id)
        return True
    
    # ========== STATISTICS ==========
    async def count_by_status(self, status: OrderStatus) -> int:
        """Количество заказов по статусу"""
        result = await self.db.execute(
            select(func.count()).select_from(Order).where(Order.status == status)
        )
        return result.scalar() or 0
    
    async def get_total_revenue(self, start_date: datetime = None, end_date: datetime = None) -> float:
        """Общая выручка за период"""
        query = select(func.sum(Order.total)).where(Order.status == OrderStatus.COMPLETED)
        
        if start_date:
            query = query.where(Order.completed_at >= start_date)
        if end_date:
            query = query.where(Order.completed_at <= end_date)
        
        result = await self.db.execute(query)
        return result.scalar() or 0.0
    
    async def get_completed_orders_count(self, start_date: datetime = None, end_date: datetime = None) -> int:
        """Количество завершённых заказов за период"""
        query = select(func.count()).select_from(Order).where(Order.status == OrderStatus.COMPLETED)
        
        if start_date:
            query = query.where(Order.completed_at >= start_date)
        if end_date:
            query = query.where(Order.completed_at <= end_date)
        
        result = await self.db.execute(query)
        return result.scalar() or 0