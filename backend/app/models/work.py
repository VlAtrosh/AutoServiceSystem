from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Work(Base):
    __tablename__ = "works"
    
    id = Column(String, primary_key=True)
    code = Column(String, unique=True, index=True)          # код работы (по классификатору)
    name = Column(String, nullable=False, index=True)       # наименование работы
    description = Column(Text)                              # описание
    
    # Цены
    price_per_hour = Column(Float, nullable=False)          # стоимость нормо-часа
    min_hours = Column(Float, default=0.5)                  # минимальное количество часов
    max_hours = Column(Float)                               # максимальное количество часов
    
    # Категория
    category = Column(String, index=True)                   # двигатель, подвеска, электрика и т.д.
    subcategory = Column(String)                            # подкатегория
    
    # Статистика
    times_performed = Column(Integer, default=0)            # сколько раз выполнялась
    average_rating = Column(Float, default=0.0)             # средняя оценка
    
    # Дополнительно
    is_active = Column(Integer, default=1)                  # 1 - активна, 0 - архив
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Work {self.code}: {self.name}>"