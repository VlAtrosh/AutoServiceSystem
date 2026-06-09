from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WorkBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    price_per_hour: float = Field(..., gt=0)
    min_hours: float = Field(default=0.5, gt=0)
    max_hours: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    subcategory: Optional[str] = None


class WorkCreate(WorkBase):
    pass


class WorkUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_per_hour: Optional[float] = Field(None, gt=0)
    min_hours: Optional[float] = Field(None, gt=0)
    max_hours: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    subcategory: Optional[str] = None
    is_active: Optional[int] = None


class WorkResponse(WorkBase):
    id: str
    times_performed: int
    average_rating: float
    is_active: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True