from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.model.models_user import Base


class UserAuth(Base):
    __tablename__ = "user_auth"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
