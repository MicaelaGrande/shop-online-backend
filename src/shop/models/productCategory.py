from sqlalchemy import Column, Integer, ForeignKey
from src.shop.db import Base


class ProductCategory(Base):
    __tablename__ = "product_category"

    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)
