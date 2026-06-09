from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.repositories.mechanic_repository import MechanicRepository
from app.repositories.order_repository import OrderRepository
from app.models.mechanic import Mechanic, MechanicStatus
from app.models.order import OrderStatus, Order


class MechanicService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.mechanic_repo = MechanicRepository(db)
        self.order_repo = OrderRepository(db)
    
    async def get_mechanic(self, mechanic_id: str) -> Optional[Mechanic]:
        """Получить механика по ID"""
        return await self.mechanic_repo.get_by_id(mechanic_id)
    
    async def get_all_mechanics(self, skip: int = 0, limit: int = 100) -> List[Mechanic]:
        """Получить всех механиков"""
        return await self.mechanic_repo.get_all(skip, limit)
    
    async def get_free_mechanics(self) -> List[Mechanic]:
        """Получить свободных механиков"""
        return await self.mechanic_repo.get_free_mechanics()
    
    async def get_available_mechanics_for_order(self, specialization: str = None) -> List[Mechanic]:
        """
        Получить доступных механиков для назначения на заказ.
        Учитывает специализацию.
        """
        mechanics = await self.mechanic_repo.get_available_mechanics()
        
        if specialization:
            mechanics = [m for m in mechanics if m.specialization.value == specialization]
        
        # Сортируем по рейтингу и загруженности
        mechanics.sort(key=lambda m: (-m.rating, m.completed_orders_count))
        
        return mechanics
    
    async def assign_mechanic(self, order_id: str, mechanic_id: str) -> Order | None:
        """Назначить механика на заказ"""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            return None
        
        order.mechanic_id = mechanic_id
        return await self.order_repo.update(order)



    async def assign_mechanic_to_order(
        self, 
        order_id: str, 
        mechanic_id: str,
        auto_assign_if_busy: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Назначить механика на заказ.
        Если механик занят и auto_assign_if_busy=False — отказ.
        """
        mechanic = await self.mechanic_repo.get_by_id(mechanic_id)
        if not mechanic:
            return {"success": False, "error": "Mechanic not found"}
        
        # Проверяем, свободен ли механик
        if mechanic.status != MechanicStatus.FREE:
            if auto_assign_if_busy:
                # Можно назначить, но с предупреждением
                pass
            else:
                return {"success": False, "error": f"Mechanic is {mechanic.status.value}"}
        
        # Назначаем механика на заказ
        order = await self.order_repo.assign_mechanic(order_id, mechanic_id)
        if not order:
            return {"success": False, "error": "Order not found"}
        
        # Меняем статус механика на занят
        await self.mechanic_repo.change_status(mechanic_id, MechanicStatus.BUSY)
        
        return {
            "success": True,
            "order_id": order_id,
            "mechanic_id": mechanic_id,
            "mechanic_name": mechanic.user.name if mechanic.user else None
        }
    
    async def complete_order_and_free_mechanic(
        self, 
        order_id: str, 
        mechanic_id: str,
        actual_hours: float,
        earned_amount: float
    ) -> Optional[Mechanic]:
        """
        Завершить заказ и освободить механика.
        Обновляет статистику механика.
        """
        # Сначала меняем статус заказа
        order = await self.order_repo.update_status(order_id, OrderStatus.COMPLETED)
        if not order:
            return None
        
        # Обновляем статистику механика
        mechanic = await self.mechanic_repo.increment_completed_orders(
            mechanic_id, actual_hours, earned_amount
        )
        
        # Освобождаем механика
        await self.mechanic_repo.change_status(mechanic_id, MechanicStatus.FREE)
        
        return mechanic
    
    async def get_mechanic_load(self) -> Dict[str, Any]:
        """
        Получить текущую загрузку механиков.
        """
        mechanics = await self.mechanic_repo.get_all()
        
        return {
            "total_mechanics": len(mechanics),
            "free_count": len([m for m in mechanics if m.status == MechanicStatus.FREE]),
            "busy_count": len([m for m in mechanics if m.status == MechanicStatus.BUSY]),
            "on_break_count": len([m for m in mechanics if m.status == MechanicStatus.ON_BREAK]),
            "mechanics": [
                {
                    "id": m.id,
                    "name": m.user.name if m.user else "Unknown",
                    "specialization": m.specialization.value,
                    "status": m.status.value,
                    "current_orders": 1 if m.status == MechanicStatus.BUSY else 0,
                    "rating": m.rating
                }
                for m in mechanics
            ]
        }
    
    async def get_mechanic_performance(
        self, 
        mechanic_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Получить детальную производительность механика за период.
        """
        mechanic = await self.mechanic_repo.get_by_id(mechanic_id)
        if not mechanic:
            return {}
        
        # Получаем заказы механика за период
        orders = await self.order_repo.get_by_mechanic_id(mechanic_id)
        
        if start_date:
            orders = [o for o in orders if o.completed_at and o.completed_at >= start_date]
        if end_date:
            orders = [o for o in orders if o.completed_at and o.completed_at <= end_date]
        
        completed_orders = [o for o in orders if o.status == OrderStatus.COMPLETED]
        
        total_revenue = sum(o.total for o in completed_orders)
        avg_order_value = total_revenue / len(completed_orders) if completed_orders else 0
        
        return {
            "mechanic_id": mechanic.id,
            "name": mechanic.user.name if mechanic.user else "Unknown",
            "specialization": mechanic.specialization.value,
            "rating": mechanic.rating,
            "total_orders_completed": len(completed_orders),
            "total_revenue": total_revenue,
            "average_order_value": avg_order_value,
            "total_hours_worked": mechanic.total_hours_worked,
            "total_earned": mechanic.total_earned,
            "efficiency_rate": (mechanic.total_earned / mechanic.total_hours_worked) if mechanic.total_hours_worked > 0 else 0
        }
    
    async def update_mechanic_rating(self, mechanic_id: str) -> Optional[Mechanic]:
        """
        Автоматически пересчитать рейтинг механика на основе:
        - Количество завершённых заказов (40%)
        - Средний рейтинг отзывов (30%)
        - Эффективность (заработано/часы) (30%)
        """
        mechanic = await self.mechanic_repo.get_by_id(mechanic_id)
        if not mechanic:
            return None
        
        # Заглушка для отзывов — позже можно реализовать отдельную модель Review
        avg_review_rating = 5.0  # временно, пока нет отзывов
        
        # Расчёт компонентов рейтинга
        orders_score = min(mechanic.completed_orders_count / 100, 5.0)
        efficiency = (mechanic.total_earned / mechanic.total_hours_worked) if mechanic.total_hours_worked > 0 else 0
        efficiency_score = min(efficiency / 2000, 5.0)  # 2000 руб/час = максимум
        
        # Итоговый рейтинг
        new_rating = (
            orders_score * 0.4 +
            avg_review_rating * 0.3 +
            efficiency_score * 0.3
        )
        
        new_rating = round(max(1.0, min(5.0, new_rating)), 1)
        
        mechanic.rating = new_rating
        return await self.mechanic_repo.update(mechanic)