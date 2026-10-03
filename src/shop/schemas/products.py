from pydantic import BaseModel, Field, field_validator, model_validator
from decimal import Decimal
from typing import Optional
from .category import CategoryPublic
from .media import MediaPublic


class ProductPublic(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    is_active: bool
    categories: list[CategoryPublic]
    media: list[MediaPublic]
    is_on_sale: bool
    sale_price: Optional[Decimal] = None

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal = Field(gt=0)  # Debe ser price>0
    category_ids: list[int] = Field(default_factory=list)
    is_on_sale: bool = False
    sale_price: Optional[Decimal] = None

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

        return name.strip()
    
    @model_validator(mode="after")
    def validate_sale(self):
        if not self.is_on_sale:
            self.sale_price = None
            return self

        if self.sale_price is None:
            raise ValueError(
                "El precio de oferta es obligatorio cuando la oferta está activa"
            )

        if self.sale_price <= 0:
            raise ValueError("El precio de oferta debe ser mayor que cero")

        if self.sale_price >= self.price:
            raise ValueError(
                "El precio de oferta debe ser menor que el precio normal"
            )

        return self

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(default=None, gt=0)
    category_ids: Optional[list[int]] = None
    is_on_sale: Optional[bool] = None
    sale_price: Optional[Decimal] = Field(default=None, gt=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, name):
        if name is None:
            return name

        if not name.strip():
            raise ValueError("El nombre del producto no puede estar vacío")

        if len(name.strip()) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres")

        if len(name) > 100:
            raise ValueError("El nombre no puede superar los 100 caracteres")

        return name.strip()
