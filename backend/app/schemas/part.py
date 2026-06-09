from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PartBase(BaseModel):
    code: str
    article: str
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    purchase_price: Optional[float] = Field(None, ge=0)
    quantity: int = Field(default=0, ge=0)
    warehouse: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None


class PartCreate(PartBase):
    pass


class PartUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    purchase_price: Optional[float] = Field(None, ge=0)
    quantity: Optional[int] = Field(None, ge=0)
    reserved: Optional[int] = Field(None, ge=0)
    warehouse: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    is_active: Optional[int] = None


class PartResponse(PartBase):
    id: str
    reserved: int
    is_active: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True