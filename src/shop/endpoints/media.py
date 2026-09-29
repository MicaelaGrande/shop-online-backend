import cloudinary.uploader
import logging
import json
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Form
from sqlalchemy.orm import Session
from PIL import Image, UnidentifiedImageError
from src.settings import settings

from src.shop.db import get_db
from src.shop.dependencies import get_current_admin
from src.shop.models import Admin, Media, Product
from src.shop.schemas.media import MediaPublic, MediaOrderUpdate
from src.shop.schemas.products import ProductPublic, ProductUpdate
from src.shop.services.product_service import update_product_with_media

MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_IMAGE_WIDTH = 5000
MAX_IMAGE_HEIGHT = 5000
MAX_IMAGE_PIXELS = 25_000_000


logger = logging.getLogger(__name__)
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
    media_count = db.query(Media).filter(
        Media.product_id == product_id).count()

    if media_count >= settings.MAX_PRODUCT_MEDIA:
        raise HTTPException(
            status_code=409,
            detail="El producto ya tiene el máximo de "
            f"{settings.MAX_PRODUCT_MEDIA} imágenes",
        )

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


@router.patch(
    "/{product_id}/media/order",
    response_model=list[MediaPublic],
)
def update_media_order(
    product_id: int,
    new_order_media: MediaOrderUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado",
        )

    requested_ids = new_order_media.media_ids

    if len(requested_ids) != len(set(requested_ids)):
        raise HTTPException(
            status_code=400,
            detail="No se permiten imágenes repetidas",
        )

    product_media = (
        db.query(Media)
        .filter(Media.product_id == product_id)
        .all()
    )

    existing_ids = {media.id for media in product_media}
    requested_id_set = set(requested_ids)

    if existing_ids != requested_id_set:
        raise HTTPException(
            status_code=400,
            detail="La lista debe contener exactamente las imágenes del producto",
        )

    media_by_id = {
        media.id: media
        for media in product_media
    }

    for sort_order, media_id in enumerate(requested_ids):
        media = media_by_id[media_id]
        media.sort_order = sort_order

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return sorted(
        product_media,
        key=lambda media: media.sort_order,
    )


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


@router.patch(
    "/{product_id}/complete",
    response_model=ProductPublic,
)
def update_product_with_media_endpoint(
    product_id: int,
    product_data: str = Form(...),
    media_to_delete: str = Form("[]"),
    images: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado",
        )

    try:
        parsed_product_data = json.loads(product_data)
        parsed_media_to_delete = json.loads(media_to_delete)

        product_in = ProductUpdate.model_validate(parsed_product_data)

    except (json.JSONDecodeError, TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Los datos del producto no son válidos",
        )

    if not isinstance(parsed_media_to_delete, list):
        raise HTTPException(
            status_code=400,
            detail="La lista de imágenes a eliminar no es válida",
        )

    try:
        updated_product, public_ids_to_delete = update_product_with_media(
            product=product,
            product_in=product_in,
            new_images=images,
            media_to_delete=parsed_media_to_delete,
            db=db,
        )

        db.commit()
        db.refresh(updated_product)

        for public_id in public_ids_to_delete:
            try:
                result = cloudinary.uploader.destroy(
                    public_id,
                    resource_type="image",
                )

                if result.get("result") not in {"ok", "not found"}:
                    logger.warning(
                        "No se pudo borrar imagen de Cloudinary %s: %s",
                        public_id,
                        result,
                    )
            except Exception:
                logger.exception(
                    "Falló el borrado de imagen de Cloudinary %s",
                    public_id,
                )

        return updated_product

    except Exception:
        db.rollback()
        raise
    finally:
        for image in images:
            image.file.close()