from pydantic import BaseModel
class CategoryPublic(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

from pydantic import BaseModel, field_validator


class CategoryPublic(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
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