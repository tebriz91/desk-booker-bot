from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from services.bookings_list_generator import (
    generate_list_of_current_bookings_by_telegram_id,
    generate_list_of_all_current_bookings_by_room_id)

booking_management_router = Router()

@booking_management_router.message(Command("view_my_bookings"))
async def command_get_current_bookings_by_telegram_id(
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

@booking_management_router.message(Command("view_all_bookings"))
async def command_get_all_current_bookings_by_room_id(
    message: Message,
    session: AsyncSession,
    date_format: str,
    date_format_short: str) -> None:
    room_id = 1
    bookings = await generate_list_of_all_current_bookings_by_room_id(
        session,
        date_format,
        date_format_short,
        room_id)
    await message.answer(text=bookings)