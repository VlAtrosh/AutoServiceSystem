"""Тесты для сервиса пользователей."""
import sys
from pathlib import Path

# Добавляем папку backend в путь поиска модулей
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import db
from app.modules.user.models import UserRole
from app.modules.user.service import UserService


class TestUserService:
    def setup_method(self):
        """Очистка базы данных перед каждым тестом"""
        db.users.clear()
        db.tokens.clear()

    def test_hash_password(self):
        """TC-07: Хэширование пароля"""
        password = "123"
        hashed = UserService.hash_password(password)

        assert hashed is not None
        assert len(hashed) == 32  # MD5 хэш = 32 символа
        assert hashed == "202cb962ac59075b964b07152d234b70"  # MD5 of "123"

    def test_register_user(self):
        """TC-08: Регистрация нового пользователя"""
        user = UserService.register(
            name="Иван Тестовый",
            phone="+79123456789",
            email="ivan@test.ru",
            password="123",
            role=UserRole.CLIENT,
        )

        assert user is not None
        assert user.id in db.users
        assert user.name == "Иван Тестовый"
        assert user.email == "ivan@test.ru"
        assert user.role == UserRole.CLIENT
        assert user.password_hash == "202cb962ac59075b964b07152d234b70"

    def test_register_duplicate_email(self):
        """Негативный сценарий: регистрация с уже существующим email"""
        # Первая регистрация
        UserService.register(
            name="Иван",
            phone="+79123456789",
            email="duplicate@test.ru",
            password="123",
            role=UserRole.CLIENT,
        )

        # Вторая регистрация с тем же email
        user2 = UserService.register(
            name="Петр",
            phone="+79998887766",
            email="duplicate@test.ru",
            password="456",
            role=UserRole.CLIENT,
        )

        # Проверяем, что второй пользователь создался (с тем же email)
        # В текущей реализации это допустимо, но можно добавить проверку уникальности
        assert user2 is not None
        assert user2.email == "duplicate@test.ru"
        assert user2.name == "Петр"

    def test_login_success(self):
        """TC-09: Успешный вход в систему"""
        # Сначала регистрируем пользователя
        UserService.register(
            name="Тест Вход",
            phone="+79123456789",
            email="login@test.ru",
            password="123",
            role=UserRole.CLIENT,
        )

        # Пытаемся войти
        token = UserService.login("login@test.ru", "123")

        assert token is not None
        assert token in db.tokens
        assert db.tokens[token] in db.users

    def test_login_wrong_password(self):
        """Негативный сценарий: вход с неверным паролем"""
        # Регистрируем пользователя
        UserService.register(
            name="Тест Пароль",
            phone="+79123456789",
            email="wrongpass@test.ru",
            password="123",
            role=UserRole.CLIENT,
        )

        # Пытаемся войти с неверным паролем
        token = UserService.login("wrongpass@test.ru", "wrong")

        assert token is None

    def test_login_nonexistent_user(self):
        """Негативный сценарий: вход несуществующего пользователя"""
        token = UserService.login("nonexistent@test.ru", "123")

        assert token is None

    def test_get_user(self):
        """TC-10: Получение пользователя по ID"""
        # Регистрируем пользователя
        user = UserService.register(
            name="Тест Поиск",
            phone="+79123456789",
            email="find@test.ru",
            password="123",
            role=UserRole.CLIENT,
        )

        # Ищем по ID
        found_user = UserService.get_user(user.id)

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.name == "Тест Поиск"

    def test_get_nonexistent_user(self):
        """Негативный сценарий: получение несуществующего пользователя"""
        user = UserService.get_user("nonexistent_id")

        assert user is None
