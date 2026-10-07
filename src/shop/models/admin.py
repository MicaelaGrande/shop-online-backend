from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shop.db import Base


class Admin(Base):
    __tablename__= "admin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    whatsapp_phone = Column(String(30), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
