from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ClientBase(BaseModel):
    discount: Optional[float] = 0
    status: Optional[str] = "active"
    preferred_contact: Optional[str] = "phone"
    receive_notifications: Optional[bool] = True

class ClientCreate(BaseModel):
    user_id: str
    discount: Optional[float] = 0
    status: Optional[str] = "active"
    preferred_contact: Optional[str] = "phone"
    receive_notifications: Optional[bool] = True

class ClientUpdate(BaseModel):
    discount: Optional[float] = None
    status: Optional[str] = None
    preferred_contact: Optional[str] = None
    receive_notifications: Optional[bool] = None

class ClientResponse(BaseModel):
    id: str
    user_id: str
    discount: float
    total_spent: float
    total_orders: int
    last_visit: Optional[datetime] = None
    status: str
    created_at: datetime
    
    # Дополнительные поля из User
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    
    class Config:
        from_attributes = True