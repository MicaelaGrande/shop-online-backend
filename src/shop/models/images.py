from sqlalchemy import Column, Integer, String, ForeignKey
from src.shop.db import Base


class ProductMedia(Base):
    __tablename__ = "products_media"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    url = Column(String(255), nullable=False)
    alt_text = Column(String(200), nullable=True)
