import logging
from io import BytesIO

import cloudinary.uploader
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.orm import Session

from src.shop.db import get_db
from src.shop.dependencies import get_current_admin
from src.shop.models import Admin, Banner, BannerSettings
from src.shop.schemas.banner import (
    BannerPublic,
    BannerSettingsUpdate,
    BannerConfigPublic,
)

router = APIRouter(prefix="/banners", tags=["banners"])
logger = logging.getLogger(__name__)

MAX_SIZE = 5 * 1024 * 1024
MAX_PIXELS = 25_000_000
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


def prepare_image(image: UploadFile) -> bytes:
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Las imágenes deben ser JPG, PNG o WEBP")

    image.file.seek(0, 2)
    size = image.file.tell()
    image.file.seek(0)

    if size > MAX_SIZE:
        raise HTTPException(413, "Cada imagen puede pesar hasta 5 MB")

    try:
        with Image.open(image.file) as original:
            if original.format not in {"JPEG", "PNG", "WEBP"}:
                raise HTTPException(400, "Formato de imagen no permitido")

            width, height = original.size
            if width * height > MAX_PIXELS or max(width, height) > 5000:
                raise HTTPException(413, "Las dimensiones son demasiado grandes")

            original.verify()

        image.file.seek(0)

        with Image.open(image.file) as original:
            clean = ImageOps.exif_transpose(original)
            mode = "RGBA" if "A" in clean.getbands() else "RGB"
            output = BytesIO()
            clean.convert(mode).save(output, format="WEBP", quality=88)
            return output.getvalue()

    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(400, "El archivo no es una imagen válida")
    finally:
        image.file.seek(0)


def get_layout_mode(db: Session) -> str:
    settings = db.get(BannerSettings, 1)
    return settings.layout_mode if settings else "grid"


@router.get("/", response_model=BannerConfigPublic)
def get_banners(db: Session = Depends(get_db)):
    banners = db.query(Banner).order_by(Banner.position).all()
    return {
        "layout_mode": get_layout_mode(db),
        "banners": banners,
    }


@router.put("/settings", response_model=BannerConfigPublic)
def update_banner_settings(
    settings_in: BannerSettingsUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    settings = db.get(BannerSettings, 1)

    if settings is None:
        settings = BannerSettings(id=1, layout_mode=settings_in.layout_mode)
        db.add(settings)
    else:
        settings.layout_mode = settings_in.layout_mode

    db.commit()
    db.refresh(settings)

    banners = db.query(Banner).order_by(Banner.position).all()
    return {
        "layout_mode": settings.layout_mode,
        "banners": banners,
    }


@router.put("/{position}", response_model=BannerPublic)
def replace_banner(
    position: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    if position not in (0, 1, 2):
        raise HTTPException(400, "La posición debe ser 0, 1 o 2")

    uploaded_public_id = None
    old_banner = db.query(Banner).filter(Banner.position == position).first()

    try:
        image_bytes = prepare_image(image)
        result = cloudinary.uploader.upload(
            BytesIO(image_bytes),
            folder="banners",
            resource_type="image",
            format="webp",
        )
        uploaded_public_id = result["public_id"]

        if old_banner:
            old_public_id = old_banner.public_id
            old_banner.url = result["secure_url"]
            old_banner.public_id = uploaded_public_id
        else:
            old_public_id = None
            old_banner = Banner(
                url=result["secure_url"],
                public_id=uploaded_public_id,
                position=position,
            )
            db.add(old_banner)

        db.commit()
        db.refresh(old_banner)

        if old_public_id:
            try:
                cloudinary.uploader.destroy(old_public_id, resource_type="image")
            except Exception:
                logger.warning("No se pudo borrar %s", old_public_id)

        return old_banner

    except HTTPException:
        db.rollback()
        if uploaded_public_id:
            cloudinary.uploader.destroy(uploaded_public_id, resource_type="image")
        raise
    except Exception as error:
        db.rollback()
        if uploaded_public_id:
            try:
                cloudinary.uploader.destroy(uploaded_public_id, resource_type="image")
            except Exception:
                logger.warning("No se pudo limpiar %s", uploaded_public_id)
        logger.exception("Error al guardar el banner")
        raise HTTPException(502, "No se pudo guardar el banner") from error
    finally:
        image.file.close()


@router.delete("/{position}", status_code=204)
def delete_banner(
    position: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    if position not in (0, 1, 2):
        raise HTTPException(400, "La posición debe ser 0, 1 o 2")

    banner = db.query(Banner).filter(Banner.position == position).first()
    if banner is None:
        raise HTTPException(404, "No existe un banner en esa posición")

    public_id = banner.public_id
    db.delete(banner)
    db.flush()

    remaining = db.query(Banner).order_by(Banner.position).all()
    db.query(Banner).update(
        {Banner.position: Banner.position + 3},
        synchronize_session=False,
    )
    db.flush()

    for new_position, item in enumerate(remaining):
        item.position = new_position

    db.commit()

    try:
        cloudinary.uploader.destroy(public_id, resource_type="image")
    except Exception:
        logger.warning("No se pudo borrar %s", public_id)