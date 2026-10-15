from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Literal


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
    
class AssignedAdminInOrder(BaseModel):
    name: str
    whatsapp_phone: str


class OrderItemCreated(BaseModel):
    name: str
    quantity: int
    unit_price: Decimal


class OrderCreated(BaseModel):
    id: int
    status: str
    created_at: datetime
    comments: str | None = None
    assigned_admin: AssignedAdminInOrder
    items: list[OrderItemCreated]
    
class OrderAdminListItem(BaseModel):
    id: int
    customer_name: str
    customer_phone: str
    created_at: datetime
    status: str
    total: Decimal
    assigned_admin_id: int
    assigned_admin_name: str


class OrderAdminDetail(OrderAdminListItem):
    customer_address: str | None = None
    comments: str | None = None
    processed_by_admin_name: str | None = None
    items: list[OrderItemCreated]
    
class OrderStatusUpdate(BaseModel):
    status: Literal["paid", "cancelled"]


class OrderStatusUpdated(BaseModel):
    id: int
    status: str
    processed_by_admin_id: int
    processed_by_admin_name: str