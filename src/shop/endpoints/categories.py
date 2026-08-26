from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.shop.db import get_db
from src.shop.models import Category
from src.shop.schemas.category import CategoryCreate, CategoryPublic

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryPublic])
def get_categories(db: Session = Depends(get_db)):
    return (
        db.query(Category)
        .filter(Category.is_active == True)
        .order_by(Category.name.asc())
        .all()
    )


@router.post("/", response_model=CategoryPublic)
def create_category(category_in: CategoryCreate, db: Session = Depends(get_db)):
    existing = (db.query(Category).filter(Category.name == category_in.name)).first()

    if existing:
        raise HTTPException(
            status_code=400, detail="Ya existe una categoria con ese nombre"
        )
    category = Category(name=category_in.name)
    db.add(category)
    db.commit()
    db.refresh(category)

    return category
