from pydantic import BaseModel

class MediaPublic(BaseModel):
    url: str

    class Config:
        orm_mode = True