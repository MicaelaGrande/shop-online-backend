from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session


from src.shop.db import get_db
from src.shop.models import Product, Category, Admin
from src.shop.schemas.products import ProductPublic, ProductCreate, ProductUpdate
from src.shop.dependencies import get_current_admin
from src.shop.services.product_service import update_product_data

router = APIRouter(prefix="/products", tags=["products"])


# Nota mental de funcionamiento: Cuando llegue un GET a /products, llamá a get_products función
@router.get("/", response_model=list[ProductPublic])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_active == True).all()
    return products


@router.get("/search", response_model=list[ProductPublic])
def search_products(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    search_term = q.strip()

    if not search_term:
        return []

    return (
        db.query(Product)
        .filter(
            Product.is_active == True,
            or_(
                Product.name.ilike(f"%{search_term}%"),
                Product.description.ilike(f"%{search_term}%"),
            ),
        )
        .all()
    )

@router.get("/admin/deleted/search", response_model=list[ProductPublic])
def search_deleted_products(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    search_term = q.strip()

    if not search_term:
        return []

    return (
        db.query(Product)
        .filter(
            Product.is_active == False,
            or_(
                Product.name.ilike(f"%{search_term}%"),
                Product.description.ilike(f"%{search_term}%"),
            ),
        )
        .all()
    )

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
        .filter(Product.name.lower() == product_in.name.lower(), Product.is_active == True)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400, detail="Ya existe un producto activo con ese nombre"
        )

    product = Product(
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        is_on_sale=product_in.is_on_sale,
        sale_price=product_in.sale_price,
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


@router.get(
    "/admin/deleted",
    response_model=list[ProductPublic],
)
def get_deleted_products(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    return db.query(Product).filter(Product.is_active == False).all()


@router.patch("/{product_id}", response_model=ProductPublic)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado",
        )

    update_product_data(product, product_in, db)
    try:
        db.commit()
        db.refresh(product)
    except Exception:
        db.rollback()
        raise

    return product


@router.patch(
    "/{product_id}/deactivate",
    response_model=ProductPublic,
)
def deactivate_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado",
        )

    product.is_active = False
    db.commit()
    db.refresh(product)

    return product


@router.patch(
    "/{product_id}/restore",
    response_model=ProductPublic,
)
def restore_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado",
        )

    product.is_active = True
    db.commit()
    db.refresh(product)

    return product
