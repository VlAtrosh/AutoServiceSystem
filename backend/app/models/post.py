from sqlalchemy import Column, String, Integer, Enum as SQLEnum
from app.core.database import Base
import enum


class PostStatus(str, enum.Enum):
    FREE = "free"
    BUSY = "busy"
    MAINTENANCE = "maintenance"


class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)  # "Пост №1", "Пост №2"
    status = Column(String, default="free")
    current_order_id = Column(String, nullable=True)  # ID заказа, который сейчас на посту