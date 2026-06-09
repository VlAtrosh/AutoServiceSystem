# app/schemas/payment.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.payment import PaymentStatus, PaymentMethod


class PaymentCreate(BaseModel):
    order_id: str
    amount: float = Field(..., gt=0)
    method: PaymentMethod = PaymentMethod.CASH
    comment: Optional[str] = None


class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    method: Optional[PaymentMethod] = None
    transaction_id: Optional[str] = None
    receipt_number: Optional[str] = None
    comment: Optional[str] = None


class PaymentResponse(BaseModel):
    id: str
    order_id: str
    client_id: str
    amount: float
    method: PaymentMethod
    status: PaymentStatus
    payment_date: datetime
    confirmed_at: Optional[datetime]
    transaction_id: Optional[str]
    receipt_url: Optional[str]
    receipt_number: Optional[str]
    comment: Optional[str]
    received_by: Optional[str]
    
    class Config:
        from_attributes = True


class PaymentConfirm(BaseModel):
    transaction_id: Optional[str] = None
    receipt_number: Optional[str] = None


class PaymentRefund(BaseModel):
    reason: Optional[str] = None


class PaymentStatistics(BaseModel):
    total_paid: float
    total_pending: float
    total_refunded: float
    payments_count: int
    by_method: dict