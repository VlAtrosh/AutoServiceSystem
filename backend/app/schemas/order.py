from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.order import OrderStatus


# ========== ORDER ITEM (сначала определяем OrderItemResponse) ==========
class OrderItemResponse(BaseModel):
    id: str
    name: str
    quantity: float
    price: float
    total: float
    
    class Config:
        from_attributes = True


# ========== ORDER ==========
class OrderBase(BaseModel):
    client_id: str
    car_info: str

class OrderCreate(BaseModel):
    car_id: str

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    mechanic_id: Optional[str] = None

class OrderResponse(BaseModel):
    id: str
    number: str
    client_id: str
    car_info: str
    status: OrderStatus
    total: float
    mechanic_id: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []  # ← теперь работает, так как OrderItemResponse определён выше
    
    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    id: str
    number: str
    client_id: str
    car_info: str
    status: OrderStatus
    total: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== ORDER ITEM CREATE ==========
class OrderItemBase(BaseModel):
    order_id: str
    item_type: str
    item_id: str
    name: str
    quantity: float
    price: float

class OrderItemCreate(OrderItemBase):
    pass


# ========== REQUEST/RESPONSE ==========
class OrderItemAdd(BaseModel):
    item_id: str
    hours: Optional[float] = Field(default=1.0, gt=0)
    quantity: Optional[float] = Field(default=1.0, gt=0)

class OrderStatusUpdate(BaseModel):
    new_status: OrderStatus

class OrderStatusResponse(BaseModel):
    id: str
    number: str
    client_id: str
    car_info: str
    status: OrderStatus
    total: float
    mechanic_id: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True