from pydantic import BaseModel, field_validator


class CategoryPublic(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True


class CategoryName(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, name):
        name = name.strip().lower()

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