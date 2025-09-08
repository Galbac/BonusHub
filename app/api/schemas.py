from datetime import datetime

from pydantic import BaseModel

from app.model.models_user import VerificationStatus


class UserBase(BaseModel):
    tg_id: int | None
    first_name: str
    last_name: str
    patronymic: str
    business: str


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    tg_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None
    business: str | None = None
    verification_status: VerificationStatus | None = None


class UserOut(UserBase):
    id: int
    verification_status: VerificationStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True
