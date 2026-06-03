from fastapi import APIRouter, Body, Depends, HTTPException

from ...core.dependencies import get_current_user
from ..user.models import UserRole
from .excel_export import ExcelExporter

router = APIRouter(prefix="/api/v1/integration", tags=["integration"])


@router.post("/export-excel")
def export_excel(data: dict = Body(...), current_user=Depends(get_current_user)):
    if current_user.role != UserRole.DIRECTOR:
        raise HTTPException(status_code=403, detail="Access denied")

    filename = ExcelExporter.export_report(data)
    return {"status": "ok", "filename": filename}
