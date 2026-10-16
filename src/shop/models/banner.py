from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shop.db import Base


class Banner(Base):
    __tablename__ = "banners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    public_id: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    
class BannerSettings(Base):
    __tablename__ = "banner_settings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        default=1,
    )
    layout_mode: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="grid",
        server_default="grid",
    )