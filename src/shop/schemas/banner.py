from typing import Literal
from pydantic import BaseModel


class BannerPublic(BaseModel):
    id: int
    url: str
    position: int

    class Config:
        from_attributes = True
        
class BannerSettingsUpdate(BaseModel):
    layout_mode: Literal["grid", "carousel"]


class BannerConfigPublic(BaseModel):
    layout_mode: Literal["grid", "carousel"]
    banners: list[BannerPublic]