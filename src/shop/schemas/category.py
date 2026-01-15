from pydantic import BaseModel
class CategoryPublic(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True