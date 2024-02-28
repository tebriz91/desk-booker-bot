from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from routers.user.router import user_router

from database.orm_queries import orm_select_room_id_by_name, orm_select_rooms

from keyboards.booking_kb import create_kb_with_room_names
from keyboards.utils.callback_btns import get_callback_btns

from services.bookings_list_generator import (
    generate_list_of_current_bookings_by_telegram_id,
    generate_list_of_all_current_bookings_by_room_id)

#* Process command /view_my_bookings
@user_router.message(Command("view_my_bookings"))
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

#* Process command /view_all_bookings
@user_router.message(Command("view_all_bookings"))
async def process_command_view_all_bookings(
    message: Message,
    session: AsyncSession,
    ):
    # Retrieve rooms from the database
    rooms_orm_obj = await orm_select_rooms(session)
    rooms = [rooms.name for rooms in rooms_orm_obj]
    # Create an inline keyboard with available room names as buttons
    keyboard = create_kb_with_room_names(rooms, 1, last_btn='Cancel')

    await message.answer(
    text='Choose a room:',
    reply_markup=keyboard
    )

#* Process the last button (Cancel)
@user_router.callback_query(F.data == "last_btn")
async def process_callback_query_from_cancel_button(query: CallbackQuery):
    await query.message.edit_text("Process has been canceled")
    await query.answer()

#* Process the room button
@user_router.callback_query(F.data.in_(['A', 'B', 'C']))
async def process_callback_query_from_room_button(
    query: CallbackQuery,
    session: AsyncSession,
    date_format: str,
    date_format_short: str) -> None:
    room_name = query.data
    room_id = await orm_select_room_id_by_name(session, room_name)
    bookings = await generate_list_of_all_current_bookings_by_room_id(
        session,
        date_format,
        date_format_short,
        room_id)
    await query.message.edit_text(
        text=bookings,
        # Add a keyboard with the "Back" and "Cancel" buttons
        reply_markup=get_callback_btns(
                btns={
                    "Back": f"back_",
                    "Cancel": f"last_btn",
                },
                sizes=(2,)
            ),)
    await query.answer()

#* Process the back button
#TODO: Refactor. Add callback factory and states
@user_router.callback_query(F.data.startswith("back_"))
async def process_callback_query_from_back_button(query: CallbackQuery, session: AsyncSession):
    # Retrieve rooms from the database
    rooms_orm_obj = await orm_select_rooms(session)
    rooms = [rooms.name for rooms in rooms_orm_obj]
    # Create an inline keyboard with available room names as buttons
    keyboard = create_kb_with_room_names(rooms, 1, last_btn='Cancel')

    await query.message.edit_text(
    text='Choose a room:',
    reply_markup=keyboard
    )
    await query.answer()