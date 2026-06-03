from enum import Enum


class UserRole(str, Enum):
    CLIENT = "client"
    RECEIVER = "receiver"
    MECHANIC = "mechanic"
    DIRECTOR = "director"


class User:
    def __init__(
        self,
        id: str,
        name: str,
        phone: str,
        email: str,
        role: UserRole,
        password_hash: str,
    ):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.role = role
        self.password_hash = password_hash
