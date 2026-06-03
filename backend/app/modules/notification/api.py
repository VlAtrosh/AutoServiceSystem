from fastapi import APIRouter

from .service import NotificationService

router = APIRouter(prefix="/api/v1/notification", tags=["notification"])


@router.post("/test-sms")
def test_sms(phone: str, message: str):
    result = NotificationService.send_sms(phone, message)
    return {"status": "ok" if result else "failed"}
