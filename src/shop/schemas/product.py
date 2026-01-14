from pydantic import BaseModel
from decimal import Decimal
from typing import List

class ProductPublic(BaseModel):
    id: int
    name: str
    description: str
    price: Decimal
    categories: List[str]
    images: List[str]