from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CarBase(BaseModel):
    brand: str
    model: str
    year: Optional[int] = None
    vin: Optional[str] = None
    license_plate: str
    color: Optional[str] = None
    engine_type: Optional[str] = None
    engine_volume: Optional[float] = None
    horsepower: Optional[int] = None
    transmission: Optional[str] = None
    drive_unit: Optional[str] = None
    mileage: Optional[int] = None
    purchase_date: Optional[datetime] = None
    last_service_date: Optional[datetime] = None
    next_service_date: Optional[datetime] = None
    comment: Optional[str] = None

class CarCreate(CarBase):
    pass

class CarUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    vin: Optional[str] = None
    license_plate: Optional[str] = None
    color: Optional[str] = None
    client_id: Optional[str] = None
    engine_type: Optional[str] = None
    engine_volume: Optional[float] = None
    horsepower: Optional[int] = None
    transmission: Optional[str] = None
    drive_unit: Optional[str] = None
    mileage: Optional[int] = None
    purchase_date: Optional[datetime] = None
    last_service_date: Optional[datetime] = None
    next_service_date: Optional[datetime] = None
    comment: Optional[str] = None

class CarResponse(CarBase):
    id: str
    client_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True