from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from src.shop.db import get_db
from src.shop.models import Product, Category, Admin
from src.shop.schemas.products import ProductPublic, ProductCreate, ProductUpdate
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

    changes = product_in.model_dump(exclude_unset=True)

    if "name" in changes:
        existing = (
            db.query(Product)
            .filter(
                Product.name == changes["name"],
                Product.id != product_id,
                Product.is_active == True,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Ya existe otro producto activo con ese nombre",
            )

        product.name = changes["name"]

    if "description" in changes:
        product.description = changes["description"]

    if "price" in changes:
        product.price = changes["price"]

    if "category_ids" in changes:
        categories = (
            db.query(Category).filter(Category.id.in_(changes["category_ids"])).all()
        )

        if len(categories) != len(changes["category_ids"]):
            raise HTTPException(
                status_code=400,
                detail="Una o más categorías no existen",
            )

        inactive = [category.name for category in categories if not category.is_active]

        if inactive:
            raise HTTPException(
                status_code=400,
                detail=f"Categorías inactivas: {', '.join(inactive)}",
            )

        product.categories = categories

    final_is_on_sale = changes.get("is_on_sale", product.is_on_sale)
    final_price = changes.get("price", product.price)
    final_sale_price = changes.get("sale_price", product.sale_price)

    if final_is_on_sale:
        if final_sale_price is None:
            raise HTTPException(
                status_code=400,
                detail="El precio de oferta es obligatorio",
            )

        if final_sale_price >= final_price:
            raise HTTPException(
                status_code=400,
                detail="El precio de oferta debe ser menor que el precio normal",
            )

        product.is_on_sale = True
        product.sale_price = final_sale_price
    else:
        product.is_on_sale = False
        product.sale_price = None

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
