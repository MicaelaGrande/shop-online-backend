from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from src.shop.db import get_db
from src.shop.models import Product, Category, Admin
from src.shop.schemas.products import ProductPublic, ProductCreate
from src.shop.dependencies import get_current_admin

router = APIRouter(prefix="/products", tags=["products"])


# Nota mental de funcionamiento: Cuando llegue un GET a /products, llamá a get_products función
@router.get("/", response_model=list[ProductPublic])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_active == True).all()
    return products


@router.get("/{product_id}", response_model=ProductPublic)
def get_products(product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active == True)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.post("/", response_model=ProductPublic)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    existing = (
        db.query(Product)
        .filter(Product.name == product_in.name, Product.is_active == True)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400, detail="Ya existe un producto activo con ese nombre"
        )

    product = Product(
        name=product_in.name, description=product_in.description, price=product_in.price
    )

    if product_in.category_ids:
        categories = (
            db.query(Category).filter(Category.id.in_(product_in.category_ids)).all()
        )
        product.categories = categories

        if len(categories) != len(product_in.category_ids):
            raise HTTPException(
                status_code=400, detail="Una o más categorías no existen"
            )

        inactive = [c.name for c in categories if not c.is_active]
        if inactive:
            raise HTTPException(
                status_code=400, detail=f"Categorias inactivas: {', '.join(inactive)}"
            )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


