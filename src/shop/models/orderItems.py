from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship, mapped_column, Mapped
from src.shop.db import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer, nullable=False, default=1)

     # Precio congelado al momento de la orden
    price_at_time = Column(Numeric(10, 2), nullable=False)
    
    # Precio actual del producto
    current_price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
