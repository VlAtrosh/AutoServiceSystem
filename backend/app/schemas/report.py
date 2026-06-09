from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal


class RevenueReportRequest(BaseModel):
    from_date: date
    to_date: date


class DailyRevenue(BaseModel):
    date: date
    total: float
    orders_count: int


class RevenueReportResponse(BaseModel):
    from_date: date
    to_date: date
    total_revenue: float
    orders_count: int
    avg_check: float
    daily_breakdown: List[DailyRevenue]


class PopularWork(BaseModel):
    work_id: str
    work_name: str
    times_performed: int
    total_revenue: float
    price_per_hour: float


class PopularWorksResponse(BaseModel):
    from_date: date
    to_date: date
    works: List[PopularWork]


class MechanicLoad(BaseModel):
    mechanic_id: str
    mechanic_name: str
    completed_orders: int
    total_hours: float
    total_earned: float
    efficiency: float  # earned per hour


class MechanicsLoadResponse(BaseModel):
    from_date: date
    to_date: date
    mechanics: List[MechanicLoad]


class SummaryReportResponse(BaseModel):
    total_revenue: float
    total_orders: int
    avg_check: float
    total_mechanics: int
    total_works_performed: int
    period_days: int