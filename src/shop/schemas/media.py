from pydantic import BaseModel

class MediaPublic(BaseModel):
    id: int
    url: str
    public_id: str

    class Config:
        from_attributes = True