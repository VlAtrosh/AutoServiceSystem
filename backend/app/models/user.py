from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.order import Order


class UserRole(str, enum.Enum):
    CLIENT = 'client'
    RECEIVER = 'receiver'
    MECHANIC = 'mechanic'
    DIRECTOR = 'director'


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    
    last_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    middle_name = Column(String)
    passport_data = Column(String)
    inn = Column(String)
    
    phone = Column(String)
    address = Column(String)
    registration_address = Column(String)
    
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="client")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    
    comment = Column(String)

    # Связи
    client_profile = relationship("Client", back_populates="user", uselist=False)
    mechanic_profile = relationship("Mechanic", back_populates="user", uselist=False)
    cars = relationship("Car", back_populates="client")