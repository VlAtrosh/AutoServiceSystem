from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    ACCEPTED = "accepted"
    DIAGNOSTICS = "diagnostics"
    WAITING_APPROVAL = "waiting_approval"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    COMPLETED = "completed"


class OrderItem:
    def __init__(
        self, item_type: str, id: str, name: str, quantity: float, price: float
    ):
        self.type = item_type
        self.id = id
        self.name = name
        self.quantity = quantity
        self.price = price
        self.total = quantity * price


class Order:
    def __init__(self, id: str, number: str, client_id: str, car_info: str):
        self.id = id
        self.number = number
        self.client_id = client_id
        self.car_info = car_info
        self.status = OrderStatus.ACCEPTED
        self.items: list[OrderItem] = []
        self.mechanic_id = ""
        self.created_at = datetime.now()
        self.completed_at: datetime | None = None
        self.total = 0.0
