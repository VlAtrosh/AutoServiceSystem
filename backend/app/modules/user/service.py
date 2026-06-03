import hashlib
import uuid

from ...core.database import db
from .models import User, UserRole


class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.md5(password.encode()).hexdigest()

    @staticmethod
    def register(
        name: str, phone: str, email: str, password: str, role: UserRole
    ) -> User:
        user_id = str(uuid.uuid4())[:8]
        user = User(
            id=user_id,
            name=name,
            phone=phone,
            email=email,
            role=role,
            password_hash=UserService.hash_password(password),
        )
        db.users[user_id] = user
        return user

    @staticmethod
    def login(email: str, password: str):
        for user in db.users.values():
            if user.email == email and user.password_hash == UserService.hash_password(
                password
            ):
                token = str(uuid.uuid4())
                db.tokens[token] = user.id
                print(f"[LOGIN] Token saved: {token} for user {user.id}")
                return token
        print(f"[LOGIN] Login failed for email: {email}")
        return None

    @staticmethod
    def get_user(user_id: str):
        return db.users.get(user_id)
