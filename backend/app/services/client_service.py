from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.client import Client
from app.repositories.client_repository import ClientRepository


class ClientService:
    
    @staticmethod
    async def add_order_total(db: AsyncSession, client_id: str, amount: float) -> Client:
        """Добавляет сумму заказа в общую статистику клиента"""
        client_repo = ClientRepository(db)
        client = await client_repo.get_by_id(client_id)
        
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        client.total_spent += amount
        client.total_orders += 1
        client.last_visit = datetime.now()
        
        # Обновляем скидку
        ClientService._update_discount(client)
        
        await client_repo.update(client)
        return client
    
    @staticmethod
    def _update_discount(client: Client) -> None:
        """Автоматический расчёт скидки на основе общей суммы"""
        if client.total_spent >= 100000:
            client.discount = 10
        elif client.total_spent >= 50000:
            client.discount = 5
        elif client.total_spent >= 20000:
            client.discount = 3
        else:
            client.discount = 0
    
    @staticmethod
    async def get_client_statistics(db: AsyncSession, client_id: str) -> dict:
        """Получить статистику клиента"""
        client_repo = ClientRepository(db)
        client = await client_repo.get_by_id(client_id)
        if not client:
            return {}
        
        return {
            "total_spent": client.total_spent,
            "total_orders": client.total_orders,
            "discount": client.discount,
            "last_visit": client.last_visit,
            "next_discount_level": ClientService._get_next_discount_level(client.total_spent)
        }
    
    @staticmethod
    def _get_next_discount_level(total_spent: float) -> dict:
        """Подсказывает, сколько осталось до следующей скидки"""
        if total_spent < 20000:
            return {"level": 3, "needed": 20000 - total_spent}
        elif total_spent < 50000:
            return {"level": 5, "needed": 50000 - total_spent}
        elif total_spent < 100000:
            return {"level": 10, "needed": 100000 - total_spent}
        else:
            return {"level": "max", "needed": 0}