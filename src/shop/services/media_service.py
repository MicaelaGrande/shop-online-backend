from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from src.settings import settings

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_IMAGE_WIDTH = 5000
MAX_IMAGE_HEIGHT = 5000
MAX_IMAGE_PIXELS = 25_000_000

def validate_image(image: UploadFile) -> None:
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no permitido: {image.filename}",
        )

    image.file.seek(0, 2)
    file_size = image.file.tell()
    image.file.seek(0)

    if file_size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"La imagen supera los 5 MB: {image.filename}",
        )

    try:
        uploaded_image = Image.open(image.file)
        width, height = uploaded_image.size

        if (
            width > MAX_IMAGE_WIDTH
            or height > MAX_IMAGE_HEIGHT
            or width * height > MAX_IMAGE_PIXELS
        ):
            raise HTTPException(
                status_code=413,
                detail=f"Dimensiones no permitidas: {image.filename}",
            )

        uploaded_image.verify()
        image.file.seek(0)

    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail=f"El archivo no es una imagen válida: {image.filename}",
        )