from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.appointment import Appointment

router = APIRouter()

class AppointmentCreate(BaseModel):
    client_name: str
    phone: str
    car_info: str
    appointment_date: Optional[date] = None
    description: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: str
    client_name: str
    phone: str
    car_info: str
    appointment_date: Optional[date] = None
    description: Optional[str] = None
    status: str
    created_at: datetime

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать заявку на ремонт"""
    appointment_id = str(uuid.uuid4())
    
    await db.execute(
        insert( Appointment).values(
            id=appointment_id,
            client_name=appointment.client_name,
            phone=appointment.phone,
            car_info=appointment.car_info,
            appointment_date=appointment.appointment_date,
            description=appointment.description,
            status="new",
            created_at=datetime.now()
        )
    )
    await db.commit()
    
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    return result.scalar_one()

@router.get("/", response_model=List[AppointmentResponse])
async def get_appointments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Получить список заявок (только админ)"""
    if current_user.role != UserRole.DIRECTOR:
        raise HTTPException(status_code=403, detail="Not enough rights")
    
    result = await db.execute(select(Appointment).order_by(Appointment.created_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()