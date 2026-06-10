from sqlalchemy import Column, String, Date, Text, DateTime
from app.core.database import Base
from datetime import datetime

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(String, primary_key=True)
    client_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    car_info = Column(String, nullable=False)
    appointment_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String, default="new")
    created_at = Column(DateTime, default=datetime.now)