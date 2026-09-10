from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.settings import settings
from src.shop.db import get_db
from src.shop.models import Admin
from src.shop.schemas.auth import AdminPublic
from src.shop.security import verify_password


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AdminPublic)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    admin = (
        db.query(Admin)
        .filter(Admin.email == form_data.username)
        .first()
    )

    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not admin or not verify_password(
        form_data.password,
        admin.password_hash,
    ):
        raise invalid_credentials

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrador inactivo",
        )

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    token_payload = {
        "sub": str(admin.id),
        "exp": expires_at,
    }

    access_token = jwt.encode(
        token_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return admin