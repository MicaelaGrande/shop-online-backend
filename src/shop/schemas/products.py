from pydantic import BaseModel
from decimal import Decimal
from typing import List
from .category import CategoryPublic
from .media import MediaPublic


class ProductPublic(BaseModel):
    id: int
    name: str
    description: str
    price: Decimal
    categories: List[CategoryPublic]
    media: List[MediaPublic]

    class Config:
        orm_mode = True
