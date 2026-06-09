from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum


class PaymentStatus(str, enum.Enum):
    PENDING = 'pending'
    PAID = 'paid'
    PARTIAL = 'partial'
    REFUNDED = 'refunded'
    CANCELLED = 'cancelled'


class PaymentMethod(str, enum.Enum):
    CASH = 'cash'
    CARD = 'card'
    ONLINE = 'online'
    BANK_TRANSFER = 'transfer'


class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey('orders.id'), nullable=False)
    client_id = Column(String, ForeignKey('clients.id'), nullable=False)
    
    amount = Column(Float, nullable=False)
    method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.CASH)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    payment_date = Column(DateTime, default=datetime.now)
    confirmed_at = Column(DateTime, nullable=True)
    
    transaction_id = Column(String, nullable=True)
    payment_system = Column(String, nullable=True)
    receipt_url = Column(String, nullable=True)
    receipt_number = Column(String, nullable=True)
    received_by = Column(String, ForeignKey('users.id'), nullable=True)
    comment = Column(String, nullable=True)
    
    order = relationship('Order', back_populates='payments')
    client = relationship('Client', back_populates='payments')
    receiver = relationship('User', foreign_keys=[received_by])