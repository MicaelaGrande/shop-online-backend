from pydantic import BaseModel, Field

from src.shop.schemas.products import ProductPublic


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, gt=0)


class CartItemPublic(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductPublic

    class Config:
        from_attributes = True