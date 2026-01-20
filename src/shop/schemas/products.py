from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from typing import List, Optional
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


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal = Field(gt=0)  # Debe ser price>0
    category_ids: Optional[List[int]] = []
    media_urls: Optional[List[str]] = []

    @field_validator("name")
    @classmethod
    def validate_name(cls, name):
        if not name or not name.strip():
            raise ValueError("El nombre del producto no puede estar vacío")

        if len(name.strip()) < 3:
            raise ValueError("El nombre del producto debe tener al menos 3 caracteres")

        if len(name) > 100:
            raise ValueError(
                "El nombre del producto no puede superar los 100 caracteres"
            )

        return name.strip().lower()

    @field_validator("media_urls")
    @classmethod
    def validate_media_urls(cls, urls):
        for url in urls:
            if not url or not url.strip():
                raise ValueError("URL/s invalida/s")
        return urls
