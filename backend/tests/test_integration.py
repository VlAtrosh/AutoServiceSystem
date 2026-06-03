import requests

BASE_URL = "http://localhost:8000/api/v1"


class TestIntegration:
    def setup_method(self):
        """Подготовка перед тестом"""
        self.client_token = None
        self.mechanic_token = None
        self.order_id = None

    def test_full_workflow(self):
        """INT-01: Полный цикл работы автосервиса"""

        # Шаг 1: Авторизация клиента
        login_response = requests.post(
            f"{BASE_URL}/user/login", json={"email": "test@mail.ru", "password": "123"}
        )
        assert login_response.status_code == 200
        self.client_token = login_response.json()["access_token"]
        print("[TEST] Шаг 1: Клиент авторизован")

        # Шаг 2: Создание заказа
        create_response = requests.post(
            f"{BASE_URL}/order/create",
            headers={"Authorization": f"Bearer {self.client_token}"},
            json={"client_id": "client1", "car_info": "BMW X5 2022"},
        )
        assert create_response.status_code == 200
        self.order_id = create_response.json()["order_id"]
        print(f"[TEST] Шаг 2: Заказ создан, ID = {self.order_id}")

        # Шаг 3: Авторизация механика
        mechanic_login = requests.post(
            f"{BASE_URL}/user/login",
            json={"email": "mechanic@mail.ru", "password": "123"},
        )
        assert mechanic_login.status_code == 200
        self.mechanic_token = mechanic_login.json()["access_token"]
        print("[TEST] Шаг 3: Механик авторизован")

        mechanic_headers = {"Authorization": f"Bearer {self.mechanic_token}"}

        # Шаг 4: Добавление работы
        work_response = requests.post(
            f"{BASE_URL}/order/{self.order_id}/add-work",
            headers=mechanic_headers,
            json={"work_id": "w1", "hours": 2},
        )
        assert work_response.status_code == 200
        print("[TEST] Шаг 4: Работа добавлена")

        # Шаг 5: Добавление запчасти
        part_response = requests.post(
            f"{BASE_URL}/order/{self.order_id}/add-part",
            headers=mechanic_headers,
            json={"part_id": "p1", "quantity": 1},
        )
        assert part_response.status_code == 200
        print("[TEST] Шаг 5: Запчасть добавлена")

        # Шаг 6: Цепочка смены статусов
        # 6a: ACCEPTED → DIAGNOSTICS
        status_response = requests.put(
            f"{BASE_URL}/order/{self.order_id}/status?new_status=diagnostics",
            headers=mechanic_headers,
        )
        assert status_response.status_code == 200
        print("[TEST] Шаг 6a: Статус diagnostics")

        # 6b: DIAGNOSTICS → IN_PROGRESS
        status_response = requests.put(
            f"{BASE_URL}/order/{self.order_id}/status?new_status=in_progress",
            headers=mechanic_headers,
        )
        assert status_response.status_code == 200
        print("[TEST] Шаг 6b: Статус in_progress")

        # 6c: IN_PROGRESS → READY
        status_response = requests.put(
            f"{BASE_URL}/order/{self.order_id}/status?new_status=ready",
            headers=mechanic_headers,
        )
        assert status_response.status_code == 200
        print("[TEST] Шаг 6c: Статус ready -> SMS отправлено")

        # Шаг 7: Проверка списка заказов
        orders_response = requests.get(
            f"{BASE_URL}/order/orders",
            headers={"Authorization": f"Bearer {self.client_token}"},
        )
        assert orders_response.status_code == 200
        orders = orders_response.json()
        found = any(order["id"] == self.order_id for order in orders)
        assert found
        print("[TEST] Шаг 7: Заказ в списке")

        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
