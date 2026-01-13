from sqlalchemy import Column, Boolean, Integer, String
from src.shop.db import Base
from sqlalchemy.orm import relationship, mapped_column, Mapped

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)

    # La relacion entre tablas Category-Product es con una tabla intermedia pura, sin atributos por eso se usa asi relationship
    products= relationship("Product", secondary="product_category", back_populates="categories" )
