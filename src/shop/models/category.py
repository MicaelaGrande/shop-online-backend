from sqlalchemy import Column, Boolean, Integer, String
from src.shop.db import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
