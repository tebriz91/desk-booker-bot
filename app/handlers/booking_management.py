from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from services.bookings_list_generator import generate_html_formatted_string_with_users_bookings

booking_management_router = Router()

@booking_management_router.message(Command("view_my_bookings"))
async def command_get_bookings_by_telegram_id(message: Message, session: AsyncSession, date_format: str, date_format_short: str):
    telegram_id = message.from_user.id
    telegram_name = message.from_user.username
    bookings_fstring = await generate_html_formatted_string_with_users_bookings(
        session,
        date_format,
        date_format_short,
        telegram_id,
        telegram_name)
    await message.answer(text=bookings_fstring)