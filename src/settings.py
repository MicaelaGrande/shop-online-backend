from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación"""

    # Base de datos
    DB_FILENAME: str = "sqlite:///./shop.db"

    # Configuración del servidor
    DEBUG_MODE: bool = True

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    AUTH_COOKIE_NAME: str = "mixshop_admin_session"
    AUTH_COOKIE_SECURE: bool = False
    AUTH_COOKIE_SAMESITE: str = "lax"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
