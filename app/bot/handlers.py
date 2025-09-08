from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from app.core.config import settings
from app.db.session import asyncSessionLocal

bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()


class Form(StatesGroup):
    name = State()
    surname = State()
    patronymic = State()
    business = State()


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 Мой профиль", callback_data="profile")],
            [InlineKeyboardButton(text="📝 Выполнить задание", callback_data="task")],
            [InlineKeyboardButton(text="🛍 Магазин клуба", callback_data="shop")],
            [InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")],
        ]
    )


@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    from app.api.crud import get_user_by_tg

    await state.clear()
    async with asyncSessionLocal() as db:
        user = await get_user_by_tg(db, tg_id=message.from_user.id)
        if user:
            return await message.answer(
                f"С возвращением, <b>{user.first_name}</b>! Выберите одно из действий ниже:",
                reply_markup=main_menu(),
            )
    await message.answer(
        "Привет! Чтобы продолжить, нужно заполнить форму. Нажми 'Готов' или напиши 'готов'.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Готов")]], resize_keyboard=True
        ),
    )


@dp.message(F.text.lower() == "готов")
async def begin_registration(message: Message, state: FSMContext):
    async with asyncSessionLocal() as db:
        from app.api.crud import get_user_by_tg

        user = await get_user_by_tg(db, tg_id=message.from_user.id)
        if user:
            return await fallback(message)

    await state.set_state(Form.name)
    await message.answer("Как вас зовут? Напишите только имя в сообщении.")


@dp.message(Form.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(Form.surname)
    await message.answer("Укажите только вашу фамилию.")


@dp.message(Form.surname)
async def process_surname(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(Form.patronymic)
    await message.answer("Напишите ваше отчество.")


@dp.message(Form.patronymic)
async def process_patronymic(message: Message, state: FSMContext):
    await state.update_data(patronymic=message.text)
    await state.set_state(Form.business)
    await message.answer(
        "Напишите название вашего бизнеса, которым руководите или в котором работаете."
    )


@dp.message(Form.business)
async def process_business(message: Message, state: FSMContext):
    from app.api.crud import get_user_by_tg, update_user, create_user

    await state.update_data(business=message.text)
    data = await state.get_data()
    async with asyncSessionLocal() as db:
        existing = await get_user_by_tg(db, tg_id=message.from_user.id)
        if existing:
            await update_user(db, existing, data)
        else:
            await create_user(db, tg_id=message.from_user.id, **data)
    await message.answer(
        "✅ Ваша заявка на регистрацию отправлена!\n\n"
        "Администратор проверит ваши данные и активирует аккаунт. "
        "Как только проверка будет завершена, вы получите уведомление "
        "и сможете пользоваться всеми функциями бота.\n\n"
        "Спасибо за ожидание!",
        reply_markup=main_menu(),
    )
    await state.clear()


@dp.callback_query(F.data == "contacts")
async def show_contacts(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Меню", callback_data="menu")]]
    )
    await callback.message.edit_text(
        "Если у вас возникли вопросы или предложения — свяжитесь с нами:\n\n"
        "📧 Email: support@laribaclub.com\n"
        "💬 Telegram: @manager\n"
        "🌐 Сайт: laribaclub.com\n\n"
        "Ответим в течение 24 часов",
        reply_markup=kb,
    )


@dp.callback_query(F.data == "menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите одно из действий ниже:", reply_markup=main_menu()
    )


@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    await callback.answer(
        "Здесь будет информация о профиле (в разработке).", show_alert=True
    )


@dp.callback_query(F.data == "task")
async def task(callback: CallbackQuery):
    await callback.answer("Здесь будут задания (в разработке).", show_alert=True)


@dp.callback_query(F.data == "shop")
async def shop(callback: CallbackQuery):
    await callback.answer("Здесь будет магазин клуба (в разработке).", show_alert=True)


@dp.message()
async def fallback(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Меню", callback_data="menu")]]
    )
    await message.answer(
        "Я не понимаю эту команду. Используйте кнопки меню для навигации.",
        reply_markup=kb,
    )
