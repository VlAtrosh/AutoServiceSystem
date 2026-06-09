from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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