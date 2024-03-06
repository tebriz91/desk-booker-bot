from datetime import datetime

from aiogram import F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from sqlalchemy.ext.asyncio import AsyncSession

from config_data.config import BotOperationConfig

from enums.button_labels import ButtonLabel

from keyboards.callbacks import CBFBook, CBFUtilButtons

from states.user import FSMBooking

from routers.user.router import user_router

from database.orm_queries import (
    orm_select_booking_by_desk_id_and_date,
    orm_select_booking_by_telegram_id_and_date,
    orm_select_room_id_by_name,
    orm_select_rooms,
    orm_select_desks_by_room_name,
    orm_select_desk_id_by_name,
    orm_insert_booking)

from keyboards.book_kb import (
    create_kb_with_dates,
    create_kb_with_room_names,
    create_kb_with_desk_names)

#* Process /book command in default state
@user_router.message(Command('book'), StateFilter(default_state))
async def process_command_book_in_default_state(
    message: Message,
    state: FSMContext,
    config: BotOperationConfig):
    # Create an inline keyboard with the function create_inline_kb with the following parameters:
    keyboard = create_kb_with_dates(
        num_days=config.num_days,
        exclude_weekends=config.exclude_weekends,
        timezone=config.timezone,
        country_code=config.country_code,
        date_format=config.date_format,
        width=1, # Width of the keyboard
        util_buttons_order=['cancel'], # Order of utility buttons
        util_buttons_width=1, # Width for utility buttons
        cancel_btn=ButtonLabel.CANCEL.value) # Last button of the keyboard

    await message.answer(
        text='Choose a date:',
        reply_markup=keyboard)
    
    await state.set_state(FSMBooking.select_date)

#* Process /book command, if the user is already in the booking process
@user_router.message(
    Command('book'),
    StateFilter(FSMBooking.select_date,
                FSMBooking.select_room,
                FSMBooking.select_desk))
async def process_command_book_in_booking_states(message: Message):
    await message.answer("You are already in the booking process. Please finish it or cancel it.")

#* Process /book command, if the user has other unfinished process
# Catch-all handler for the /book command in any state other than the default state
@user_router.message(
    Command('book'),
    ~StateFilter(default_state))
async def process_command_book_in_non_default_state(message: Message):
    await message.answer("You have to finish or cancel other current process before using this command.")

#* Process the last button 'Cancel'
@user_router.callback_query(
    CBFUtilButtons.filter(F.action == ButtonLabel.CANCEL.value),
    StateFilter(FSMBooking.select_date,
                FSMBooking.select_room,
                FSMBooking.select_desk))
async def process_cancel_button(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text("Process canceled")
    await query.answer()
    await state.clear()

#* Process the date button
@user_router.callback_query(
    CBFBook.filter(),
    StateFilter(
        FSMBooking.select_date))
async def process_date_button(
    query: CallbackQuery,
    callback_data: CBFBook,
    session: AsyncSession,
    state: FSMContext,
    config: BotOperationConfig):
    date_string = callback_data.date
    date_format = config.date_format
    date = datetime.strptime(date_string, date_format).date() # Parse date string to datetime.date type: 'YYYY-MM-DD' to query the database
    # Check if user with the same telegram_id already has a booking for the same date
    already_booked = await orm_select_booking_by_telegram_id_and_date(session, query.from_user.id, date)
    
    if already_booked:
        await query.message.edit_text(f'You already have a booking for: {date_string}')
        await state.clear()
        await query.answer()
        
    else:
        await state.update_data(date=date)

        # Retrieve rooms from the database
        rooms_orm_obj = await orm_select_rooms(session)
        rooms = [rooms.name for rooms in rooms_orm_obj]
        # Create an inline keyboard with available room names as buttons
        
        if len(rooms) <= 7:
            keyboard = create_kb_with_room_names(
                rooms,
                width=1,
                util_buttons_order=['back', 'cancel'],
                util_buttons_width=2,
                back_btn=ButtonLabel.BACK.value,
                cancel_btn=ButtonLabel.CANCEL.value)

            await query.message.edit_text(
            text='Choose a room:',
            reply_markup=keyboard
            )
        else:
            keyboard = create_kb_with_room_names(
                rooms,
                width=2, # Width of the keyboard
                util_buttons_order=['back', 'cancel'],
                util_buttons_width=2,
                back_btn=ButtonLabel.BACK.value,
                cancel_btn=ButtonLabel.CANCEL.value)

            await query.message.edit_text(
            text='Choose a room:',
            reply_markup=keyboard
            )
        
        await state.set_state(FSMBooking.select_room)
    
#* Process the room button
@user_router.callback_query(CBFBook.filter(), StateFilter(FSMBooking.select_room))
async def process_room_button(
    query: CallbackQuery,
    callback_data: CBFBook,
    session: AsyncSession,
    state: FSMContext
    ):
    room_name = callback_data.room_name
    
    room_id = await orm_select_room_id_by_name(session, room_name)
    await state.update_data(room_id=room_id)
    
    desks_orm_obj = await orm_select_desks_by_room_name(session, room_name)
    desks = [desks.name for desks in desks_orm_obj]
    
    if len(desks) <= 7:
        keyboard = create_kb_with_desk_names(
            desks,
            width=1,
            util_buttons_order=['back', 'cancel'],
            util_buttons_width=2,
            back_btn=ButtonLabel.BACK.value,
            cancel_btn=ButtonLabel.CANCEL.value)
    else:
        keyboard = create_kb_with_desk_names(
            desks,
            width=2,
            util_buttons_order=['back', 'cancel'],
            util_buttons_width=2,
            back_btn=ButtonLabel.BACK.value,
            cancel_btn=ButtonLabel.CANCEL.value)

    await query.message.edit_text(
    text='Choose a desk:',
    reply_markup=keyboard
    )
    
    await state.set_state(FSMBooking.select_desk)
    
#* Process the desk button
@user_router.callback_query(CBFBook.filter(), StateFilter(FSMBooking.select_desk))
async def process_desk_button(
    query: CallbackQuery,
    callback_data: CBFBook,
    session: AsyncSession,
    state: FSMContext,
    config: BotOperationConfig
    ):
    date_format = config.date_format
    # Retrieve desk_name from the query, than desk_id from the database using the desk_name
    desk_name = callback_data.desk_name
    desk_id = await orm_select_desk_id_by_name(session, desk_name)

    # Retrieve date from the state, that is already of datetime.date type
    data = await state.get_data()
    date = data['date']

    # Check if the desk is already booked for the date
    already_booked = await orm_select_booking_by_desk_id_and_date(session, desk_id, date)
    if already_booked:
        await query.message.edit_text(f'The desk: {desk_name} is already booked for: {date.strftime(date_format)}')
        await state.clear()
        await query.answer()
    
    else:
        # Retrieve telegram_id from the query
        telegram_id = query.from_user.id

        # Retrieve room_id from the state
        room_id_FSM_obj = await state.get_data()
        room_id = int(room_id_FSM_obj['room_id'])
        
        # Insert booking into the database
        await orm_insert_booking(
            session,
            telegram_id,
            desk_id,
            room_id,
            date)
        
        await query.message.edit_text(f'You successfully booked desk: {desk_name} for: {date.strftime(date_format)}')
        await state.clear()
        await query.answer()
        
#* Process the last button 'Back'
@user_router.callback_query(
    CBFUtilButtons.filter(
        F.action == ButtonLabel.BACK.value),
    StateFilter(
        FSMBooking.select_room,
        FSMBooking.select_desk))
async def process_back_button(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    config: BotOperationConfig):
    current_state = await state.get_state()
    # If currently selecting a room, go back to date selection
    if current_state == FSMBooking.select_room.state:
        await state.set_state(FSMBooking.select_date)
        keyboard = create_kb_with_dates(
        num_days=config.num_days,
        exclude_weekends=config.exclude_weekends,
        timezone=config.timezone,
        country_code=config.country_code,
        date_format=config.date_format,
        width=1,
        util_buttons_order=['cancel'],
        util_buttons_width=1,
        cancel_btn=ButtonLabel.CANCEL.value)

        await query.message.edit_text(
            text='Choose a date:',
            reply_markup=keyboard)
    
    elif current_state == FSMBooking.select_desk.state:
        await state.set_state(FSMBooking.select_room)
        rooms_orm_obj = await orm_select_rooms(session)
        rooms = [rooms.name for rooms in rooms_orm_obj]
        
        if len(rooms) <= 7:
            keyboard = create_kb_with_room_names(
                rooms,
                width=1,
                util_buttons_order=['back', 'cancel'],
                util_buttons_width=2,
                back_btn=ButtonLabel.BACK.value,
                cancel_btn=ButtonLabel.CANCEL.value)

            await query.message.edit_text(
            text='Choose a room:',
            reply_markup=keyboard
            )
        else:
            keyboard = create_kb_with_room_names(
                rooms,
                width=2,
                util_buttons_order=['back', 'cancel'],
                util_buttons_width=2,
                back_btn=ButtonLabel.BACK.value,
                cancel_btn=ButtonLabel.CANCEL.value)

            await query.message.edit_text(
            text='Choose a room:',
            reply_markup=keyboard
            )
    
    await query.answer()