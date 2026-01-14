from sqlalchemy import Column, Integer, String
from src.shop.db import Base
from sqlalchemy.orm import Mapped, mapped_column


class Admin(Base):
    __tablename__= "admin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
