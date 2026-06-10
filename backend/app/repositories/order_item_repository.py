from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.order_item import OrderItem

class OrderItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_order_id(self, order_id: str):
        """Получить все позиции заказа по ID заказа"""
        result = await self.db.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        return result.scalars().all()
    
    async def delete(self, item_id: str):
        """Удалить позицию заказа по ID"""
        stmt = delete(OrderItem).where(OrderItem.id == item_id)
        await self.db.execute(stmt)
        await self.db.commit()
    
    async def delete_by_order_id(self, order_id: str):
        """Удалить все позиции заказа по ID заказа"""
        stmt = delete(OrderItem).where(OrderItem.order_id == order_id)
        await self.db.execute(stmt)
        await self.db.commit()