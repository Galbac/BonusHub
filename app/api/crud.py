from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers import bot
from app.model.model_auth import UserAuth
from app.model.models_user import User


async def create_user(db: AsyncSession, tg_id: int, **fields) -> User:
    user = User(tg_id=tg_id, **fields)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> Sequence[User]:
    q = await db.execute(select(User).offset(skip).limit(limit))
    return q.scalars().all()


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    q = await db.execute(select(User).where(User.id == user_id))
    return q.scalars().first()


async def get_user_by_tg(db: AsyncSession, tg_id: int) -> User | None:
    q = await db.execute(select(User).where(User.tg_id == tg_id))
    return q.scalars().first()


async def update_user(db: AsyncSession, user: User, data: dict) -> User:
    old_status = user.verification_status
    for key, value in data.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    if old_status != "verified" and user.verification_status == "verified":
        await bot.send_message(
            chat_id=user.tg_id,
            text=(
                "✅ Поздравляем! Ваш аккаунт успешно верифицирован!\n\n"
                "Теперь вы получили полный доступ ко всем функциям бота.\n\n"
                "🚀 Приятного использования!"
            ),
        )
    return user


async def get_user_by_username(db: AsyncSession, username: str) -> UserAuth | None:
    q = await db.execute(select(UserAuth).where(UserAuth.username == username))
    return q.scalars().first()
