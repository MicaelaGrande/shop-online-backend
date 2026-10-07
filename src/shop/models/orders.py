from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from src.shop.db import Base
from datetime import datetime
import enum


class OrderStatus(enum.Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
    customer_name = Column(String(80), nullable=False)
    customer_phone = Column(String(50), nullable=False)
    customer_address = Column(String(255), nullable=True)
    assigned_admin_id = Column(Integer, ForeignKey("admin.id"), nullable=False)
    processed_by_admin_id = Column(Integer, ForeignKey("admin.id"), nullable=True)
    comments = Column(Text, nullable=True)

    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    assigned_admin = relationship(
    "Admin",
    foreign_keys=[assigned_admin_id],
)

    processed_by_admin = relationship(
        "Admin",
        foreign_keys=[processed_by_admin_id],
    )