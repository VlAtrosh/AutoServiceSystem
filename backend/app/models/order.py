from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User


class OrderStatus(str, enum.Enum):
    ACCEPTED = "accepted"
    DIAGNOSTICS = "diagnostics"
    WAITING_APPROVAL = "waiting_approval"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    COMPLETED = "completed"


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey("orders.id"))
    client_id = Column(String, ForeignKey("users.id"))
    item_type = Column(String)
    item_id = Column(String)
    name = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    total = Column(Float)
    
    order = relationship("Order", back_populates="items")


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True)
    number = Column(String, unique=True, nullable=False)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    car_id = Column(String, ForeignKey("cars.id"), nullable=False)
    car_info = Column(String, nullable=False)
    mechanic_id = Column(String, ForeignKey("mechanics.id"), nullable=True)
    status = Column(String, default=OrderStatus.ACCEPTED.value)
    total = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    
    # Связи
    client = relationship("Client", back_populates="orders")
    car = relationship("Car", back_populates="orders")
    mechanic = relationship("Mechanic", foreign_keys=[mechanic_id], back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    payments = relationship("Payment", back_populates="order")