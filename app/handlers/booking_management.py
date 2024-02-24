from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_insert_booking, orm_select_bookings_by_telegram_id, orm_select_bookings_by_desk_id, orm_select_bookings_by_date, orm_delete_booking_by_id, orm_select_bookings_by_telegram_id_joined

from utils.logger import Logger

logger = Logger()

booking_management_router = Router()

@booking_management_router.message(Command("view_my_bookings"))
async def command_get_bookings_by_telegram_id(
    message: Message,
    session: AsyncSession,
    num_days: int, # Number of days to generate (env variable that transfered through dp.workflow_data)
    exclude_weekends: bool,
    timezone: str,
    country_code: str):
    
    telegram_id = message.from_user.id

    # for booking in bookings_obj:
    #     await message.answer(f"Booking id: {booking.id}, desk id: {booking.desk_id}, date: {booking.date}")

    bookings_obj = await orm_select_bookings_by_telegram_id_joined(session, message.from_user.id)
    
    
    
    # print(f">>>>>>>>>>>>>bookings_obj: {bookings_obj}")
    # print(f"{bookings_obj[0].desk.room.name}")
    # print(f"{bookings_obj[0].desk.name}")
    
    
    await message.answer("Your bookings:")