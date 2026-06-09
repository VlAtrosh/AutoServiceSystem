import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Client(Base):
    __tablename__ = "clients"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    discount = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)
    last_visit = Column(DateTime, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User")
    orders = relationship("Order")
    payments = relationship("Payment", back_populates="client")