from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from typing import Optional
from .category import CategoryPublic
from .media import MediaPublic


class ProductPublic(BaseModel):
    id: int
    name: str
    description: str
    price: Decimal
    categories: list[CategoryPublic]
    media: list[MediaPublic]

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal = Field(gt=0)  # Debe ser price>0
    category_ids: list[int] = Field(default_factory=list)



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

    