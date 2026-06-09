from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import date, timedelta
from typing import Optional

from app.core.dependencies import get_current_admin, get_db
from app.models.user import User
from app.services.report_service import ReportService
from app.schemas.report import (
    RevenueReportResponse, PopularWorksResponse,
    MechanicsLoadResponse, SummaryReportResponse,
    DailyRevenue, PopularWork, MechanicLoad
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/reports", tags=["Отчёты"])


@router.get("/revenue", response_model=RevenueReportResponse)
async def get_revenue_report(
    from_date: date = Query(..., description="Дата начала"),
    to_date: date = Query(..., description="Дата окончания"),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Отчёт по выручке за период (только админ)"""
    report_service = ReportService(db)
    result = await report_service.get_revenue_report(from_date, to_date)
    return result


@router.get("/popular-works", response_model=PopularWorksResponse)
async def get_popular_works(
    from_date: date = Query(..., description="Дата начала"),
    to_date: date = Query(..., description="Дата окончания"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Самые популярные работы за период (только админ)"""
    report_service = ReportService(db)
    works = await report_service.get_popular_works(from_date, to_date, limit)
    return {
        "from_date": from_date,
        "to_date": to_date,
        "works": works
    }


@router.get("/mechanics-load", response_model=MechanicsLoadResponse)
async def get_mechanics_load(
    from_date: date = Query(..., description="Дата начала"),
    to_date: date = Query(..., description="Дата окончания"),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Загрузка механиков за период (только админ)"""
    report_service = ReportService(db)
    mechanics = await report_service.get_mechanics_load(from_date, to_date)
    return {
        "from_date": from_date,
        "to_date": to_date,
        "mechanics": mechanics
    }


@router.get("/summary", response_model=SummaryReportResponse)
async def get_summary_report(
    from_date: date = Query(..., description="Дата начала"),
    to_date: date = Query(..., description="Дата окончания"),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Сводный отчёт за период (только админ)"""
    report_service = ReportService(db)
    result = await report_service.get_summary_report(from_date, to_date)
    return result