from sqlalchemy import Column, Integer, ForeignKey, Numeric
from src.shop.db import Base


class OrderItems(Base):
    __tablename__ = "orders_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey=("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey=("products.id"), nullable=False)

    quantity = Column(Integer, nullable=False, default=1)

     # Precio congelado al momento de la orden
    price_at_time = Column(Numeric(10, 2), nullable=False)
    
    # Precio actual del producto
    current_price = Column(Numeric(10, 2), nullable=False)
