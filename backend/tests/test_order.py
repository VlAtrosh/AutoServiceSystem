"""Тесты для сервиса заказов."""
import sys
from pathlib import Path

# Добавляем папку backend в путь поиска модулей
sys.path.insert(0, str(Path(__file__).parent.parent))

# Импортируем через абсолютный путь
from app.core.database import db
from app.modules.order.models import OrderStatus
from app.modules.order.service import OrderService
from app.modules.user.models import User, UserRole


class TestOrderService:
    def setup_method(self):
        """Очистка базы данных перед каждым тестом"""
        db.orders.clear()
        db.tokens.clear()
        # Добавляем тестового пользователя
        test_user = User(
            id="client1",
            name="Тест",
            phone="+79123456789",
            email="test@mail.ru",
            role=UserRole.CLIENT,
            password_hash="123",
        )
        db.users["client1"] = test_user

    def test_create_order(self):
        """TC-03: Создание заказа"""
        order = OrderService.create_order("client1", "BMW X5")

        assert order is not None
        assert order.id in db.orders
        assert order.car_info == "BMW X5"
        assert order.status == OrderStatus.ACCEPTED

    def test_add_work(self):
        """TC-04: Добавление работы в заказ"""
        order = OrderService.create_order("client1", "BMW X5")
        updated_order = OrderService.add_work(order.id, "w1", 2)

        assert updated_order is not None
        assert len(updated_order.items) == 1
        assert updated_order.items[0].name == "Oil change"
        assert updated_order.total == 2400

    def test_add_part_with_zero_quantity(self):
        """Негативный сценарий: добавление запчасти с quantity=0"""
        order = OrderService.create_order("client1", "BMW X5")
        updated_order = OrderService.add_part(order.id, "p1", 0)

        assert updated_order is not None
        assert len(updated_order.items) == 0
        assert updated_order.total == 0

    def test_change_status_valid(self):
        """Корректная смена статуса"""
        order = OrderService.create_order("client1", "BMW X5")

        result = OrderService.change_status(
            order.id, OrderStatus.DIAGNOSTICS, "mechanic"
        )
        assert result is True
        assert order.status == OrderStatus.DIAGNOSTICS

    def test_change_status_invalid(self):
        """Негативный сценарий: некорректная смена статуса"""
        order = OrderService.create_order("client1", "BMW X5")

        result = OrderService.change_status(order.id, OrderStatus.COMPLETED, "mechanic")
        assert result is False
        assert order.status == OrderStatus.ACCEPTED
