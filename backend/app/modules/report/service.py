from datetime import datetime

from ...core.database import db
from ..order.models import OrderStatus


class ReportService:
    @staticmethod
    def get_revenue_report(from_date: datetime, to_date: datetime) -> dict:
        total_revenue = 0
        orders_count = 0

        for order in db.orders.values():
            # Исправлено: объединили два if в один с and
            if (
                order.status == OrderStatus.COMPLETED
                and from_date <= order.created_at <= to_date
            ):
                total_revenue += order.total
                orders_count += 1

        avg_check = total_revenue / orders_count if orders_count > 0 else 0

        return {
            "from_date": from_date.isoformat(),
            "to_date": to_date.isoformat(),
            "total_revenue": total_revenue,
            "orders_count": orders_count,
            "avg_check": avg_check,
        }

    @staticmethod
    def get_mechanics_load_report():
        # Simplified version
        return [
            {
                "mechanic_id": "mech1",
                "name": "Ivanov",
                "completed_orders": 5,
                "total_hours": 40,
            }
        ]
