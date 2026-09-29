import logging
import cloudinary.uploader
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from collections.abc import Sequence

from src.shop.models import Category, Product, Media
from src.shop.schemas.products import ProductUpdate
from src.settings import settings
from src.shop.services.media_service import validate_image

logger = logging.getLogger(__name__)


def update_product_data(
    product: Product,
    product_in: ProductUpdate,
    db: Session,
):
    changes = product_in.model_dump(exclude_unset=True)

    if "name" in changes:
        existing = (
            db.query(Product)
            .filter(
                Product.name == changes["name"],
                Product.id != product.id,
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
            db.query(Category).filter(
                Category.id.in_(changes["category_ids"])).all()
        )

        if len(categories) != len(changes["category_ids"]):
            raise HTTPException(
                status_code=400,
                detail="Una o más categorías no existen",
            )

        inactive = [
            category.name for category in categories if not category.is_active]

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


def update_product_with_media(
    product: Product,
    product_in: ProductUpdate,
    new_images: Sequence[UploadFile],
    media_to_delete: Sequence[int],
    db: Session,
) -> tuple[Product, list[str]]:

    current_media = (
        db.query(Media)
        .filter(Media.product_id == product.id)
        .all()
    )

    media_by_id = {
        media.id: media
        for media in current_media
    }

    requested_media_ids = set(media_to_delete) #utiliza set para eliminar 

    invalid_media_ids = requested_media_ids - media_by_id.keys()

    if invalid_media_ids:
        raise HTTPException(
            status_code=400,
            detail="Una o más imágenes no pertenecen al producto",
        )

    remaining_media_count = (
        len(current_media) - len(requested_media_ids) + len(new_images)
    )

    if remaining_media_count > settings.MAX_PRODUCT_MEDIA:
        raise HTTPException(
            status_code=409,
            detail="El producto no puede tener más de "
            f"{settings.MAX_PRODUCT_MEDIA} imágenes",
        )
    for image in new_images:
        validate_image(image)
    update_product_data(product, product_in, db)

    public_ids_to_delete = [
        media_by_id[media_id].public_id for media_id in requested_media_ids
    ]
    
    uploaded_resources = []
    try:
        for image in new_images:
            image.file.seek(0)

            upload_result = cloudinary.uploader.upload(
                image.file,
                folder=f"products/{product.id}",
                resource_type="image",
            )

            uploaded_resources.append(upload_result)

            db.add(
                Media(
                    product_id=product.id,
                    url=upload_result["secure_url"],
                    public_id=upload_result["public_id"],
                )
            )
        for media_id in requested_media_ids:
            db.delete(media_by_id[media_id])



    except Exception:
        db.rollback()

        for resource in uploaded_resources:
            try:
                result = cloudinary.uploader.destroy(
                    resource["public_id"],
                    resource_type="image",
                )

                if result.get("result") not in {"ok", "not found"}:
                    logger.warning(
                        "No se pudo limpiar imagen nueva de Cloudinary %s: %s",
                        resource["public_id"],
                        result,
                    )
            except Exception:
                logger.exception(
                    "Falló la limpieza compensatoria de Cloudinary para %s",
                    resource["public_id"],
                )

        raise

    return product, public_ids_to_delete
