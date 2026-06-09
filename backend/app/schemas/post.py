from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PostBase(BaseModel):
    name: str
    status: str = "free"


class PostCreate(BaseModel):
    name: str


class PostUpdate(BaseModel):
    status: Optional[str] = None
    current_order_id: Optional[str] = None


class PostResponse(BaseModel):
    id: int
    name: str
    status: str
    current_order_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class PostOccupyRequest(BaseModel):
    order_id: str