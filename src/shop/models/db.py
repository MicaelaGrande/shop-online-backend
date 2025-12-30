from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.settings import settings

# 1. Motor de base de datos (la conexión)
engine = create_engine(
    settings.DB_FILENAME,
    connect_args={"check_same_thread": False},  # Solo para SQLite
    echo=True  # Muestra las consultas SQL en la consola
)

# 2. Factory de sesiones (para hacer consultas)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 3. Clase base para los modelos
Base = declarative_base()


# 4. Función para obtener sesiones de BD
def get_db():
    """
    Crea una sesión de base de datos.
    Se usa con Dependency Injection en FastAPI.
    """
    db = SessionLocal()
    try:
        yield db  # Entrega la sesión
    finally:
        db.close()  # La cierra automáticamente