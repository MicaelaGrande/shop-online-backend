import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.settings import settings
from src.shop.db import get_db
from src.shop.models import Admin


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la autenticación",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        admin_id = payload.get("sub")

        if admin_id is None:
            raise credentials_exception

        admin_id = int(admin_id)

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise credentials_exception

    admin = (
        db.query(Admin)
        .filter(Admin.id == admin_id)
        .first()
    )

    if admin is None:
        raise credentials_exception

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrador inactivo",
        )

    return admin