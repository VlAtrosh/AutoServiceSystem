import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.order import Order, OrderStatus, OrderItem
from app.repositories.order_repository import OrderRepository
from app.repositories.car_repository import CarRepository
import uuid


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)

    async def create_order(self, client_id: str, car_id: str, car_info: str) -> Order:
        order_id = str(uuid.uuid4())[:8]
        order = Order(
            id=order_id,
            number=f"ЗН-{order_id}",
            client_id=client_id,
            car_id=car_id,
            car_info=car_info,
            status=OrderStatus.ACCEPTED.value,
            created_at=datetime.now()
        )
        return await self.order_repo.create(order)


    async def assign_mechanic(self, order_id: str, mechanic_id: str) -> Order | None:
        """Назначить механика на заказ"""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            return None
        
        order.mechanic_id = mechanic_id
        return await self.order_repo.update(order)

    async def change_status(self, order_id: str, new_status: str, user_role: str) -> Order | None:
        """Изменить статус заказа"""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            return None
        
        # Проверка прав (можно расширить)
        if user_role not in ["mechanic", "receiver", "director"]:
            raise ValueError("Not enough rights")
        
        order.status = new_status
        if new_status == "completed":
            order.completed_at = datetime.now()
        
        return await self.order_repo.update(order)



    async def add_work(self, order_id: str, work_id: str, hours: float, work_name: str, work_price: float) -> Order | None:
        """Добавить работу в заказ"""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            return None
        
        total_price = hours * work_price
        
        item = OrderItem(
            id=str(uuid.uuid4())[:8],
            order_id=order_id,
            item_type="work",
            item_id=work_id,
            name=work_name,
            quantity=hours,
            price=work_price,
            total=total_price
        )
        
        self.db.add(item)
        await self.db.flush()
        await self._recalculate_total(order)
        return order

    async def add_part(self, order_id: str, part_id: str, quantity: int) -> Order | None:
        """Добавить запчасть в заказ"""
        if quantity <= 0:
            order = await self.order_repo.get_by_id(order_id)
            return order

        order = await self.order_repo.get_by_id(order_id)
        if not order:
            return None

        part = await self.ref_repo.get_part_by_id(part_id)
        if not part:
            return None

        total_price = quantity * part.price
        
        item = OrderItem(
            id=str(uuid.uuid4())[:8],
            order_id=order_id,
            item_type="part",
            item_id=part_id,
            name=part.name,
            quantity=quantity,
            price=part.price,
            total=total_price
        )
        
        self.db.add(item)
        await self.db.flush()
        
        # Пересчитываем итоговую сумму
        await self._recalculate_total(order)
        
        return order

    
    async def _recalculate_total(self, order: Order) -> None:
        """Пересчитать общую сумму заказа"""
        items = await self.order_repo.get_order_items(order.id)
        order.total = sum(item.total for item in items)
        await self.order_repo.update(order)


    async def get_order(self, order_id: str) -> Order | None:
        """Получить заказ по ID"""
        return await self.order_repo.get_by_id(order_id)

    async def get_orders_by_client(self, client_id: str) -> list[Order]:
        """Получить все заказы клиента"""
        return await self.order_repo.get_by_client_id(client_id)

    async def get_all_orders(self) -> list[Order]:
        """Получить все заказы"""
        return await self.order_repo.get_all()