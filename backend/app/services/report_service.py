from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date, datetime
from typing import List, Dict, Any

from app.models.order import Order, OrderStatus, OrderItem
from app.models.mechanic import Mechanic
from app.models.work import Work


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_revenue_report(self, from_date: date, to_date: date) -> Dict[str, Any]:
        """Отчёт по выручке за период"""
        from_datetime = datetime.combine(from_date, datetime.min.time())
        to_datetime = datetime.combine(to_date, datetime.max.time())
        
        # Завершённые заказы за период
        result = await self.db.execute(
            select(Order)
            .where(Order.status == OrderStatus.COMPLETED.value)
            .where(Order.completed_at >= from_datetime)
            .where(Order.completed_at <= to_datetime)
        )
        orders = result.scalars().all()
        
        total_revenue = sum(o.total for o in orders)
        orders_count = len(orders)
        avg_check = total_revenue / orders_count if orders_count > 0 else 0
        
        # Разбивка по дням
        daily_breakdown = []
        current = from_date
        while current <= to_date:
            day_start = datetime.combine(current, datetime.min.time())
            day_end = datetime.combine(current, datetime.max.time())
            day_orders = [o for o in orders if day_start <= o.completed_at <= day_end]
            daily_breakdown.append({
                "date": current,
                "total": sum(o.total for o in day_orders),
                "orders_count": len(day_orders)
            })
            current = date(current.year, current.month, current.day + 1)
        
        return {
            "from_date": from_date,
            "to_date": to_date,
            "total_revenue": total_revenue,
            "orders_count": orders_count,
            "avg_check": avg_check,
            "daily_breakdown": daily_breakdown
        }
    
    async def get_popular_works(self, from_date: date, to_date: date, limit: int = 10) -> List[Dict[str, Any]]:
        """Самые популярные работы за период"""
        from_datetime = datetime.combine(from_date, datetime.min.time())
        to_datetime = datetime.combine(to_date, datetime.max.time())
        
        # Получаем заказы за период
        result = await self.db.execute(
            select(Order)
            .where(Order.status == OrderStatus.COMPLETED.value)
            .where(Order.completed_at >= from_datetime)
            .where(Order.completed_at <= to_datetime)
        )
        orders = result.scalars().all()
        
        # Собираем все позиции работ из заказов
        works_count = {}
        for order in orders:
            items_result = await self.db.execute(
                select(OrderItem).where(OrderItem.order_id == order.id)
            )
            items = items_result.scalars().all()
            for item in items:
                if item.item_type == "work":
                    if item.item_id not in works_count:
                        works_count[item.item_id] = {
                            "work_id": item.item_id,
                            "work_name": item.name,
                            "times_performed": 0,
                            "total_revenue": 0,
                            "price_per_hour": item.price
                        }
                    works_count[item.item_id]["times_performed"] += int(item.quantity)
                    works_count[item.item_id]["total_revenue"] += item.total
        
        # Сортируем по популярности
        result_list = list(works_count.values())
        result_list.sort(key=lambda x: x["times_performed"], reverse=True)
        
        return result_list[:limit]
    
    async def get_mechanics_load(self, from_date: date, to_date: date) -> List[Dict[str, Any]]:
        """Загрузка механиков за период"""
        from_datetime = datetime.combine(from_date, datetime.min.time())
        to_datetime = datetime.combine(to_date, datetime.max.time())
        
        # Получаем всех механиков
        result = await self.db.execute(select(Mechanic))
        mechanics = result.scalars().all()
        
        # Получаем заказы за период
        orders_result = await self.db.execute(
            select(Order)
            .where(Order.status == OrderStatus.COMPLETED.value)
            .where(Order.completed_at >= from_datetime)
            .where(Order.completed_at <= to_datetime)
            .where(Order.mechanic_id.isnot(None))
        )
        orders = orders_result.scalars().all()
        
        # Группируем заказы по механикам
        mechanic_stats = {}
        for mechanic in mechanics:
            mechanic_orders = [o for o in orders if o.mechanic_id == mechanic.id]
            total_hours = 0
            total_earned = 0
            for order in mechanic_orders:
                items_result = await self.db.execute(
                    select(OrderItem).where(OrderItem.order_id == order.id)
                )
                items = items_result.scalars().all()
                for item in items:
                    if item.item_type == "work":
                        total_hours += item.quantity
                total_earned += order.total
            
            mechanic_stats[mechanic.id] = {
                "mechanic_id": mechanic.id,
                "mechanic_name": mechanic.user.username if mechanic.user else mechanic.id,
                "completed_orders": len(mechanic_orders),
                "total_hours": total_hours,
                "total_earned": total_earned,
                "efficiency": total_earned / total_hours if total_hours > 0 else 0
            }
        
        return list(mechanic_stats.values())
    
    async def get_summary_report(self, from_date: date, to_date: date) -> Dict[str, Any]:
        """Сводный отчёт"""
        from_datetime = datetime.combine(from_date, datetime.min.time())
        to_datetime = datetime.combine(to_date, datetime.max.time())
        
        # Выручка
        revenue_report = await self.get_revenue_report(from_date, to_date)
        
        # Количество механиков
        result = await self.db.execute(select(func.count()).select_from(Mechanic))
        mechanics_count = result.scalar() or 0
        
        # Количество выполненных работ
        result = await self.db.execute(
            select(func.sum(OrderItem.quantity))
            .select_from(OrderItem)
            .where(OrderItem.item_type == "work")
        )
        total_works = result.scalar() or 0
        
        period_days = (to_date - from_date).days + 1
        
        return {
            "total_revenue": revenue_report["total_revenue"],
            "total_orders": revenue_report["orders_count"],
            "avg_check": revenue_report["avg_check"],
            "total_mechanics": mechanics_count,
            "total_works_performed": int(total_works),
            "period_days": period_days
        }