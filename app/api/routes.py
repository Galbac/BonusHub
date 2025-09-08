from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import crud
from app.api.crud import update_user
from app.api.schemas import UserOut, UserUpdate
from app.db.session import get_db

router = APIRouter(
    prefix="/users",
    tags=["🚀 Пользователи"],
    responses={404: {"description": "Не найдено — как чёрная дыра"}},
)


@router.get(
    "/",
    summary="Получить список пользователей",
    description="Возвращает список пользователей с пагинацией. Максимум — 100 на странице.",
    response_model=list[UserOut],
)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_users(db, skip, limit)


@router.get(
    "/{user_id}",
    summary="Получить пользователя по ID",
    description="Возвращает полную информацию о пользователе. Если не найден — 404.",
    response_model=UserOut,
)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )
    return user


@router.patch(
    "/{user_id}",
    summary="Частичное обновление пользователя",
    description="Обновляет только переданные поля. Поддерживает null-safe обновление.",
    response_model=UserOut,
)
async def patch_update_user(
    user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )
    data = user_update.model_dump(exclude_unset=True)
    return await update_user(db, user, data)
