from aiogram.types import Message
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from routers.user.router import user_router

from services.bookings_list_generator import generate_list_of_current_bookings_by_telegram_id

#* Process command /my_bookings
@user_router.message(Command("my_bookings"))
async def process_command_my_bookings(
    message: Message,
    session: AsyncSession,
    date_format: str,
    date_format_short: str) -> None:
    telegram_id = message.from_user.id
    telegram_name = message.from_user.username
    bookings = await generate_list_of_current_bookings_by_telegram_id(
        session,
        date_format,
        date_format_short,
        telegram_id,
        telegram_name)
    await message.answer(text=bookings)