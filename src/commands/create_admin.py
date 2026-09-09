from getpass import getpass

from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.shop.db import SessionLocal
from src.shop.models import Admin
from src.shop.schemas.auth import AdminCreate
from src.shop.security import hash_password


def main() -> None:
    email = input("Email del administrador: ").strip()
    password = getpass("Contraseña: ")
    password_confirmation = getpass("Repite la contraseña: ")

    if password != password_confirmation:
        print("Las contraseñas no coinciden")
        return

    try:
        admin_data = AdminCreate(email=email, password=password)
    except ValidationError as error:
        print("Los datos no son válidos:")
        print(error)
        return

    db: Session = SessionLocal()

    try:
        existing_admin = (
            db.query(Admin)
            .filter(Admin.email == admin_data.email)
            .first()
        )

        if existing_admin:
            print("Ya existe un administrador con ese email")
            return

        admin = Admin(
            email=admin_data.email,
            password_hash=hash_password(admin_data.password),
        )

        db.add(admin)
        db.commit()

        print("Administrador creado correctamente")
    finally:
        db.close()


if __name__ == "__main__":
    main()