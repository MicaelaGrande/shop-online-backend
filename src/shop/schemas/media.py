from pydantic import BaseModel

class MediaPublic(BaseModel):
    url: str
    public_id: str

    class Config:
        from_attributes = True