from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from src.shop.db import get_db
from src.shop.models import Cart, CartItem, Product
from src.shop.schemas.cart_item import CartItemCreate, CartItemPublic

router = APIRouter(prefix="/cart_items", tags=["cart_items"])

@router.post("/items", response_model=CartItemPublic)

def add_cart_item(
    item_in: CartItemCreate,
    session_id: str = Header(..., alias="X-Session-ID"),
    db: Session = Depends(get_db),
):
    product = (
        db.query(Product).filter
    )

