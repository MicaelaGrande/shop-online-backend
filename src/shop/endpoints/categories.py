from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.shop.db import get_db
from src.shop.models import Category, Admin
from src.shop.schemas.category import CategoryCreate, CategoryPublic, CategoryUpdate, CategoryStatusUpdate
from src.shop.dependencies import get_current_admin


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryPublic])
def get_categories(db: Session = Depends(get_db)):
    return (
        db.query(Category)
        .filter(Category.is_active == True)
        .order_by(Category.name.asc())
        .all()
    )


@router.patch("/{category_id}", response_model=CategoryPublic)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    duplicate = (
        db.query(Category)
        .filter(
            Category.name == category_in.name,
            Category.id != category_id,
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una categoría con ese nombre",
        )

    category.name = category_in.name

    try:
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ya existe una categoría con ese nombre",
        )

    return category


@router.post("/", response_model=CategoryPublic)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    existing = (db.query(Category).filter(
        Category.name == category_in.name)).first()

    if existing:
        raise HTTPException(
            status_code=400, detail="Ya existe una categoria con ese nombre"
        )
    category = Category(name=category_in.name)
    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.get("/admin/inactive", response_model=list[CategoryPublic])
def get_inactive_categories(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    return (
        db.query(Category)
        .filter(Category.is_active == False)
        .order_by(Category.name.asc())
        .all()
    )

@router.patch("/{category_id}/status", response_model=CategoryPublic)
def update_category_status(
    category_id: int,
    status_in: CategoryStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    category.is_active = status_in.is_active
    db.commit()
    db.refresh(category)

    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    category.products.clear()
    db.delete(category)
    db.commit()
