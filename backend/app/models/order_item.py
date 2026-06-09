from sqlalchemy import Column, String, Float, ForeignKey
from app.core.database import Base

class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey("orders.id"))
    item_type = Column(String)
    item_id = Column(String)
    name = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    total = Column(Float)