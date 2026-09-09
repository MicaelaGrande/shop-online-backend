from pydantic import BaseModel, EmailStr, Field


class AdminCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class AdminPublic(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True