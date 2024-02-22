from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import (
    orm_select_booking_by_telegram_id_and_date,
    orm_select_rooms,
    orm_select_desks_by_room_name,
    orm_select_desk_id_by_name,
    orm_insert_booking)

from keyboards.booking_kb import (
    create_kb_with_dates,
    create_kb_with_room_names,
    create_kb_with_desk_names)

booking_kb_router = Router()

class FSMBooking(StatesGroup):
    select_date = State()
    select_room = State()
    select_desk = State()

#* Process /book command in default state
@booking_kb_router.message(Command('book'), StateFilter(default_state))
async def process_book_command_in_default_state(
    message: Message,
    state: FSMContext,
    num_days: int, # Number of days to generate (env variable that transfered through dp.workflow_data)
    exclude_weekends: bool,
    timezone: str,
    country_code: str):
    
    # Create an inline keyboard with the function create_inline_kb with the following parameters:
    keyboard = create_kb_with_dates(
        num_days,
        exclude_weekends,
        timezone,
        country_code,
        1, # Width of the keyboard
        last_btn='Cancel')

    await message.answer(
        text='Choose a date:',
        reply_markup=keyboard)
    
    await state.set_state(FSMBooking.select_date)

#* Process /book command in non-default state
@booking_kb_router.message(Command('book'), ~StateFilter(default_state))
async def process_book_command_in_non_default_state(message: Message):
    await message.answer("You are already in the booking process. Please finish it or cancel it.")

#* Process the last button (Cancel)
@booking_kb_router.callback_query(F.data == "last_btn")
async def process_callback_query_1(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text("Process has been canceled")
    await query.answer()
    await state.clear()
    
#* Process the date button
@booking_kb_router.callback_query(StateFilter(FSMBooking.select_date))
async def process_callback_query_2(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext
    ):
    date = query.data.split(' ')[0] # Get the date from the callback data in format 'YYYY-MM-DD' (without Day of the week)
    
    # Check if user with the same telegram_id already has a booking for the same date
    already_booked = await orm_select_booking_by_telegram_id_and_date(session, query.from_user.id, date)
    
    if already_booked:
        await query.message.edit_text(f'You already have a booking for: {date}')
        await state.clear()
        await query.answer()
        
    else:
        await state.update_data(date=date)

        # Retrieve rooms from the database
        rooms_orm_obj = await orm_select_rooms(session)
        rooms = [rooms.name for rooms in rooms_orm_obj]
        # Create an inline keyboard with available room names as buttons
        keyboard = create_kb_with_room_names(rooms, 1, last_btn='Cancel')

        await query.message.edit_text(
        text='Choose a room:',
        reply_markup=keyboard
        )
        
        await state.set_state(FSMBooking.select_room)
    
#* Process the room button
@booking_kb_router.callback_query(StateFilter(FSMBooking.select_room))
async def process_callback_query_3(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext
    ):
    room_name = query.data
    desks_orm_obj = await orm_select_desks_by_room_name(session, room_name)
    desks = [desks.name for desks in desks_orm_obj]
    
    keyboard = create_kb_with_desk_names(desks, 1, last_btn='Cancel')

    await query.message.edit_text(
    text='Choose a desk:',
    reply_markup=keyboard
    )
    
    await state.set_state(FSMBooking.select_desk)
    
#* Process the desk button
@booking_kb_router.callback_query(StateFilter(FSMBooking.select_desk))
async def process_callback_query_4(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext
    ):
    # Retrieve telegram_id from the query
    telegram_id = query.from_user.id

    # Retrieve desk_name from the query
    desk_name = query.data
    # Retrieve desk_id from the database using the desk_name
    desk_id = await orm_select_desk_id_by_name(session, desk_name)

    # Retrieve date from the state
    data = await state.get_data()
    date = data['date']
    # Convert date variable to datetime.date type
    date = datetime.strptime(date, '%Y-%m-%d').date()

    # Insert booking into the database
    await orm_insert_booking(session, {
        "telegram_id": telegram_id,
        "desk_id": desk_id,
        "date": date})
    
    await query.message.edit_text(f'You have chosen the desk: {desk_name} for the date: {date}')
    await query.answer()
    
    await state.clear()