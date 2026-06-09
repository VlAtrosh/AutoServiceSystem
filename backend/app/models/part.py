from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Part(Base):
    __tablename__ = "parts"
    
    id = Column(String, primary_key=True)
    code = Column(String, unique=True, index=True)           # код запчасти (1C, складской)
    article = Column(String, unique=True, index=True)       # артикул производителя
    name = Column(String, nullable=False, index=True)       # наименование
    description = Column(Text)                              # описание
    
    # Цены
    price = Column(Float, nullable=False)                   # цена продажи
    purchase_price = Column(Float)                          # закупочная цена
    
    # Наличие
    quantity = Column(Integer, default=0)                   # остаток на складе
    reserved = Column(Integer, default=0)                   # зарезервировано
    warehouse = Column(String)                              # склад/стеллаж
    
    # Категория
    category = Column(String, index=True)                   # масла, фильтры, тормозные колодки и т.д.
    brand = Column(String, index=True)                      # бренд запчасти
    
    # Дополнительно
    is_active = Column(Integer, default=1)                  # 1 - активна, 0 - архив
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Part {self.article}: {self.name}>"