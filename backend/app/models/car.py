from sqlalchemy import Column, String, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Car(Base):
    __tablename__ = "cars"
    
    id = Column(String, primary_key=True)
    client_id = Column(String, ForeignKey("users.id"), nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    vin = Column(String, unique=True, nullable=True)  # ← добавить nullable=True
    license_plate = Column(String, unique=True, nullable=False)
    engine_type = Column(String, nullable=True)
    engine_volume = Column(Float, nullable=True)
    horsepower = Column(Integer, nullable=True)
    transmission = Column(String, nullable=True)
    drive_unit = Column(String, nullable=True)
    color = Column(String, nullable=True)  # ← добавить nullable=True
    mileage = Column(Integer, nullable=True)
    purchase_date = Column(DateTime, nullable=True)
    last_service_date = Column(DateTime, nullable=True)
    next_service_date = Column(DateTime, nullable=True)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    
    client = relationship("User", back_populates="cars")
    orders = relationship("Order", back_populates="car")