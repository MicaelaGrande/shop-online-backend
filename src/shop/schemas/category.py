from pydantic import BaseModel, field_validator
from enum import Enum

class CategoryIconKey(str, Enum):
    TAGS = "tags"
    SHOPPING_BAG = "shopping-bag"
    LAPTOP = "laptop"
    BLOCKS = "blocks"
    ZAP = "zap"
    SHIRT = "shirt"
    COFFEE = "coffee"
    HOUSE = "house"


class CategoryPublic(BaseModel):
    id: int
    name: str
    is_active: bool
    icon_key: CategoryIconKey

    class Config:
        from_attributes = True


class CategoryName(BaseModel):
    name: str
    icon_key: CategoryIconKey = CategoryIconKey.TAGS

    @field_validator("name")
    @classmethod
    def validate_name(cls, name):
        name = name.strip()

        if len(name) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")

        if len(name) > 50:
            raise ValueError("El nombre no puede superar los 50 caracteres")

        return name


class CategoryCreate(CategoryName):
    pass


class CategoryUpdate(CategoryName):
    pass

class CategoryStatusUpdate(BaseModel):
    is_active: bool