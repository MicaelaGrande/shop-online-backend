from pydantic import BaseModel, Field
from src.settings import settings

class MediaPublic(BaseModel):
    id: int
    url: str
    public_id: str
    sort_order: int
 
    class Config:
        from_attributes = True


class MediaOrderUpdate(BaseModel):
    media_ids: list[int] = Field(
        min_length=1,
        max_length=settings.MAX_PRODUCT_MEDIA,
    )