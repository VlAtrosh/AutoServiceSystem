from ..modules.order.models import Order, OrderStatus
from ..modules.user.models import User, UserRole


class Database:
    def __init__(self):
        print(f"[DB INIT] Database instance id: {id(self)}")
        self.users: dict = {}
        self.orders: dict = {}
        self.tokens: dict = {}
        self._init_test_data()

    def _init_test_data(self):
        test_user = User(
            id="client1",
            name="Тест Клиент",
            phone="+79123456789",
            email="test@mail.ru",
            role=UserRole.CLIENT,
            password_hash="202cb962ac59075b964b07152d234b70",
        )
        self.users["client1"] = test_user

        test_order = Order(
            id="order1",
            number="ЗН-001",
            client_id="client1",
            car_info="Toyota Camry 2020",
        )
        test_order.status = OrderStatus.COMPLETED
        test_order.total = 15000
        self.orders["order1"] = test_order

        test_mechanic = User(
            id="mechanic1",
            name="Тест Механик",
            phone="+79123456788",
            email="mechanic@mail.ru",
            role=UserRole.MECHANIC,
            password_hash="202cb962ac59075b964b07152d234b70",
        )
        self.users["mechanic1"] = test_mechanic


db = Database()
