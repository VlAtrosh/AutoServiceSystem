import uuid

from ...core.database import db
from ..reference.service import ReferenceService
from .models import Order, OrderItem, OrderStatus
from .status_machine import StatusMachine


class OrderService:
    _call_counter = 0

    @staticmethod
    def create_order(client_id: str, car_info: str) -> Order:
        order_id = str(uuid.uuid4())[:8]
        order = Order(
            id=order_id, number=f"ЗН-{order_id}", client_id=client_id, car_info=car_info
        )
        db.orders[order_id] = order
        return order

    @staticmethod
    def add_work(order_id: str, work_id: str, hours: float):
        OrderService._call_counter += 1
        print(f"[DEBUG] add_work ВЫЗОВ №{OrderService._call_counter}")
        print(f"[DEBUG] order_id={order_id}, work_id={work_id}, hours={hours}")
        order = db.orders.get(order_id)
        if not order:
            print("[DEBUG] order not found")
            return None

        print(f"[DEBUG] items count BEFORE append: {len(order.items)}")

        work = ReferenceService.get_work(work_id)
        if not work:
            print("[DEBUG] work not found")
            return None

        print(f"[DEBUG] work.price_per_hour = {work.price_per_hour}")
        total_price = hours * work.price_per_hour
        print(f"[DEBUG] total_price = {total_price}")

        item = OrderItem("work", work_id, work.name, hours, work.price_per_hour)
        print(f"[DEBUG] item.total = {item.total}")

        order.items.append(item)
        print(f"[DEBUG] items count AFTER append: {len(order.items)}")

        OrderService._recalculate_total(order)
        print(f"[DEBUG] order.total after recalc = {order.total}")

        return order

    @staticmethod
    def add_part(order_id: str, part_id: str, quantity: int):
        order = db.orders.get(order_id)
        if not order:
            return None

        # проверка quantity <= 0
        if quantity <= 0:
            return order

        part = ReferenceService.get_part(part_id)
        if not part:
            return None

        total_price = quantity * part.price
        item = OrderItem("part", part_id, part.name, quantity, total_price)
        order.items.append(item)
        OrderService._recalculate_total(order)
        return order

    @staticmethod
    def _recalculate_total(order: Order):
        print(f"[DEBUG] items in order: {[(i.name, i.total) for i in order.items]}")
        order.total = sum(item.total for item in order.items)
        print(f"[DEBUG] sum = {order.total}")

    @staticmethod
    def change_status(order_id: str, new_status: OrderStatus, user_role: str) -> bool:
        order = db.orders.get(order_id)
        if not order:
            return False
        return StatusMachine.transition(order, new_status)

    @staticmethod
    def get_order(order_id: str):
        return db.orders.get(order_id)

    @staticmethod
    def get_orders_by_client(client_id: str):
        return [o for o in db.orders.values() if o.client_id == client_id]

    @staticmethod
    def get_all_orders():
        from ...core.database import db

        return list(db.orders.values())
