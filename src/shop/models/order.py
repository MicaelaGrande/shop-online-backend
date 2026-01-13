from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from src.shop.db import Base
from datetime import datetime
import enum


class OrderStatus(enum.Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
    customer_name = Column(String(80), nullable=False)
    customer_phone = Column(String(50), nullable=False)
    customer_address = Column(String(255), nullable=True)
    comments = Column(Text, nullable=True)
