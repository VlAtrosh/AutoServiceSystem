from sqlalchemy import Column, String, Float, Integer, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum


class MechanicSpecialization(str, enum.Enum):
    ENGINE = "engine"
    TRANSMISSION = "transmission"
    SUSPENSION = "suspension"
    ELECTRICS = "electrics"
    BODY = "body"
    DIAGNOSTICS = "diagnostics"
    GENERAL = "general"


class MechanicStatus(str, enum.Enum):
    FREE = "free"
    BUSY = "busy"
    ON_BREAK = "on_break"
    OFF = "off"


class Mechanic(Base):
    __tablename__ = "mechanics"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    
    # Профессиональные данные
    specialization = Column(String, default="general")
    experience_years = Column(Float, default=0.0)
    education = Column(String)
    certificates = Column(String)
    
    # Статус
    status = Column(String, default="free")
    
    # Рейтинг
    rating = Column(Float, default=5.0)
    completed_orders_count = Column(Integer, default=0)
    total_hours_worked = Column(Float, default=0.0)
    total_earned = Column(Float, default=0.0)
    
    # Рабочие часы (JSON)
    schedule = Column(String)
    
    # Контакты
    phone = Column(String)
    email = Column(String)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    
    # Связи
    user = relationship("User", back_populates="mechanic_profile")
    orders = relationship("Order", foreign_keys="Order.mechanic_id", back_populates="mechanic")
    


    # Методы
    def is_available(self) -> bool:
        return self.status == MechanicStatus.FREE
    
    def assign_order(self):
        if self.is_available():
            self.status = MechanicStatus.BUSY
            return True
        return False
    
    def complete_order(self, hours: float, earned: float):
        self.completed_orders_count += 1
        self.total_hours_worked += hours
        self.total_earned += earned
        self.status = MechanicStatus.FREE