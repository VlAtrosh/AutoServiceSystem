from pydantic import BaseModel


class RevenueReportResponse(BaseModel):
    from_date: str
    to_date: str
    total_revenue: float
    orders_count: int
    avg_check: float


class MechanicLoadResponse(BaseModel):
    mechanic_id: str
    name: str
    completed_orders: int
    total_hours: float
