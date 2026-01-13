from sqlalchemy import Column, Boolean, Integer, String
from src.shop.db import Base
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)

    products= relationship("Product", secondary="product_category", back_populates="categories" )
