from sqlalchemy import Column, Integer, String, Numeric, Text, Boolean
from src.shop.db import Base
from sqlalchemy.orm import relationship


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)

    categories = relationship("Category", secondary="product_category", back_populates="products")
