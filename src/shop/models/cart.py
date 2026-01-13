from sqlalchemy import Column, Integer, String, DateTime
from src.shop.db import Base
from datetime import datetime
from sqlalchemy.orm import relationship, mapped_column, Mapped


class Cart(Base):
    __tablename__ = "carts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")