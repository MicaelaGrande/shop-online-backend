from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=80)
    customer_phone: str = Field(min_length=5, max_length=50)
    customer_address: str | None = None
    comments: str | None = None
    items: list[OrderItemCreate] = Field(min_length=1)
    assigned_admin_id: int