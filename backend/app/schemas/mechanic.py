from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.mechanic import MechanicSpecialization, MechanicStatus


class MechanicBase(BaseModel):
    specialization: MechanicSpecialization = MechanicSpecialization.GENERAL
    experience_years: float = Field(default=0, ge=0)
    education: Optional[str] = None
    certificates: Optional[str] = None
    schedule: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    

class MechanicStatusUpdate(BaseModel):
    status: str
    

class MechanicCreate(MechanicBase):
    user_id: str


class MechanicUpdate(BaseModel):
    specialization: Optional[MechanicSpecialization] = None
    status: Optional[MechanicStatus] = None
    experience_years: Optional[float] = Field(None, ge=0)
    education: Optional[str] = None
    certificates: Optional[str] = None
    schedule: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)


class MechanicResponse(MechanicBase):
    id: str
    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    status: MechanicStatus
    rating: float
    completed_orders_count: int
    total_hours_worked: float
    total_earned: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MechanicStatistics(BaseModel):
    completed_orders_count: int
    total_hours_worked: float
    total_earned: float
    rating: float
    average_hours_per_order: Optional[float] = None
    average_earned_per_order: Optional[float] = None