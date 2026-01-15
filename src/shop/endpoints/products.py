from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.shop.db import get_db
from src.shop.models.products import Product
from src.shop.schemas.products import ProductPublic

router = APIRouter()

#Nota mental de funcionamiento: Cuando llegue un GET a /products, llamá a get_products función
@router.get(
    "/products",
    response_model=list[ProductPublic]
)
def get_products(db: Session = Depends(get_db)):
    products = (
        db.query(Product)
        .filter(Product.is_active == True)
        .all()
    )
    return products
