from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from ...core.dependencies import get_current_user
from ..user.models import UserRole
from .service import ReportService

router = APIRouter(prefix="/api/v1/report", tags=["report"])


@router.get("/revenue")
def get_revenue(from_date: str, to_date: str, current_user=Depends(get_current_user)):
    if current_user.role != UserRole.DIRECTOR:
        raise HTTPException(status_code=403, detail="Access denied")

    f = datetime.fromisoformat(from_date)
    t = datetime.fromisoformat(to_date)
    return ReportService.get_revenue_report(f, t)
