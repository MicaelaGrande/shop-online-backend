from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Base de datos
    DB_FILENAME: str = "sqlite:///./shop.db"
    
    # Configuración del servidor
    DEBUG_MODE: bool = True


settings = Settings()
