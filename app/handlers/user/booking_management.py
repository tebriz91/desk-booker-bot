from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_insert_booking, orm_select_bookings_by_user_id, orm_select_bookings_by_desk_id, orm_select_bookings_by_date, orm_delete_booking_by_id

from utils.logger import Logger

logger = Logger()

booking_management_router = Router()

@booking_management_router.message(Command("view_my_bookings"))
async def command_get_bookings_by_user_id_handler(message: Message, session: AsyncSession):
    telegram_id = message.from_user.id
    bookings = await orm_select_bookings_by_user_id(session, telegram_id)
    for booking in bookings:
        await message.answer(f"Booking id: {booking.id}, desk id: {booking.desk_id}, date: {booking.date}")

@booking_management_router.message(F.text.startswith("/booking"))
async def command_add_booking_handler(message: Message, session: AsyncSession):
    command_name, desk_id, raw_date = message.text.split(sep=" ")
    date = datetime.strptime(raw_date, '%Y-%m-%d').date() # turn string into datetype
    telegram_id = message.from_user.id
    logger.info(f"Booking param: desk_id: {desk_id}, date: {date}, telegram_id: {telegram_id}")
    try:
        await orm_insert_booking(session, {
            "telegram_id": telegram_id,
            "desk_id": desk_id,
            "date": date
            })
        await message.answer(f"Desk with id: {desk_id} was successfully booked by user with id: {telegram_id} for date: {date}")
    except Exception as e:
        logger.error(e)
        await message.answer(f"Booking error: {e}")

