from sqlalchemy import Column, Integer, String, DateTime
from src.shop.db import Base
from datetime import datetime


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
