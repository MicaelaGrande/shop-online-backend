from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.shop.models.db import Base


class Category(Base):
    """Modelo de Categoría con subcategorías"""
    
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    
    # Clave foránea a sí misma (categoría padre)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Relaciones
    parent = relationship(
        "Category",
        remote_side=[id],
        backref="subcategories"
    )
    
    def __repr__(self):
        parent_name = self.parent.name if self.parent else "None"
        return f"<Category(id={self.id}, name='{self.name}', parent='{parent_name}')>"