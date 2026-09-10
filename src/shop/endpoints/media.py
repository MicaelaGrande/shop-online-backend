import cloudinary.uploader
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from PIL import Image, UnidentifiedImageError

from src.shop.db import get_db
from src.shop.dependencies import get_current_admin
from src.shop.models import Admin, Media, Product
from src.shop.schemas.media import MediaPublic

MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_IMAGE_WIDTH = 5000
MAX_IMAGE_HEIGHT = 5000
MAX_IMAGE_PIXELS = 25_000_000

router = APIRouter(prefix="/media_products", tags=["media"])


@router.get(
    "/{product_id}/media",
    response_model=list[MediaPublic],
)
def get_product_media(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado",
        )

    return db.query(Media).filter(Media.product_id == product_id).all()


@router.post(
    "/{product_id}/media",
    response_model=MediaPublic,
    status_code=201,
)
def upload_product_media(
    product_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado",
        )

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser JPG, PNG o WEBP",
        )

    image.file.seek(0, 2)

    file_size = image.file.tell()
    image.file.seek(0)

    if file_size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="La imagen no puede superar los 5 MB",
        )

    try:
        image.file.seek(0)
        uploaded_image = Image.open(image.file)
        width, height = uploaded_image.size
        if (
            width > MAX_IMAGE_WIDTH
            or height > MAX_IMAGE_HEIGHT
            or width * height > MAX_IMAGE_PIXELS
        ):
            raise HTTPException(
                status_code=413,
                detail="Las dimensiones de la imagen son demasiado grandes",
            )
        uploaded_image.verify()
        image.file.seek(0)
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="El archivo no es una imagen válida",
        )

    upload_result = None

    try:
        upload_result = cloudinary.uploader.upload(
            image.file,
            folder=f"products/{product_id}",
            resource_type="image",
        )

        media = Media(
            product_id=product_id,
            url=upload_result["secure_url"],
            public_id=upload_result["public_id"],
        )

        db.add(media)
        db.commit()
        db.refresh(media)

        return media

    except Exception:
        db.rollback()

        if upload_result:
            cloudinary.uploader.destroy(
                upload_result["public_id"],
                resource_type="image",
            )

        raise

    finally:
        image.file.close()


@router.delete(
    "/{product_id}/media/{media_id}",
    status_code=204,
)
def delete_product_media(
    product_id: int,
    media_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    media = (
        db.query(Media)
        .filter(
            Media.id == media_id,
            Media.product_id == product_id,
        )
        .first()
    )

    if not media:
        raise HTTPException(
            status_code=404,
            detail="Imagen no encontrada para este producto",
        )

    try:
        cloudinary.uploader.destroy(
            media.public_id,
            resource_type="image",
        )
        db.delete(media)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return None
