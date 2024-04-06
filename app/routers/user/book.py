from typing import List

from aiogram import F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from sqlalchemy.ext.asyncio import AsyncSession

from config_data.config import Config

from misc.const.button_labels import ButtonLabel

from states.user import FSMBooking

from routers.user.router import user_router

from keyboards.inline import get_inline_keyboard

from services.user.dates_generator import generate_dates
from services.user.booking_checker import check_existing_booking
from services.user.desk_assignment_checker import check_desk_assignment
from services.common.rooms_list_generator import generate_available_rooms_list
from services.common.room_plan_getter import get_room_plan_by_room_name
from services.common.desks_list_generator import generate_desks_list
from services.user.desk_booker import desk_booker

from utils.logger import Logger

logger = Logger()


#* Process /book command in default state
@user_router.message(Command('book'), StateFilter(default_state))
async def process_command_book_in_default_state(
    message: Message,
    state: FSMContext,
    config: Config):
    
    # Get the config data
    c = config.bot_operation
    
    # Check advanced mode and update state
    if c.advanced_mode:
        await state.update_data(advanced_mode=True)
    else:
        await state.update_data(advanced_mode=False)
    
    # Generate dates
    dates: List[str] = await generate_dates(
        c.num_days,
        c.exclude_weekends,
        c.timezone,
        c.country_code,
        c.date_format)
    
    keyboard = get_inline_keyboard(
        buttons=dates,
        width=1,
        util_buttons=[
            ButtonLabel.CANCEL.value,],
        width_util=1)

    await message.answer(
        text='Select date',
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


#* Process 'Cancel' button
@user_router.callback_query(
    F.data == ButtonLabel.CANCEL.value,
    StateFilter(FSMBooking.select_date,
                FSMBooking.select_room,
                FSMBooking.select_desk))
async def process_cancel_button(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text("Process canceled")
    await query.answer()
    await state.clear()


#* Process date button
@user_router.callback_query(StateFilter(FSMBooking.select_date))
async def process_date_button(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    config: Config):
    date = query.data
    date_format = config.bot_operation.date_format
    telegram_id=query.from_user.id
    
    existing_booking = await check_existing_booking(
    session,
    telegram_id,
    date,
    date_format)
    
    try:
        if existing_booking:
            await query.message.edit_text(text=f"{existing_booking}")
            await state.clear()
            await query.answer()
            logger.info(f">>>>>>>>>>>>>existing_booking: {existing_booking}")
        # Check if the user has assigned desk for the weekday of the selected date
        if not existing_booking:
            desk_assignment = await check_desk_assignment(
                session,
                telegram_id,
                date,
                date_format)
            logger.info(f">>>>>>>>>>>>>desk_assignment: {desk_assignment}")
            if desk_assignment:
                await query.message.edit_text(text=f"{desk_assignment}")
                await state.clear()
                await query.answer()
        
            else:
                rooms = await generate_available_rooms_list(session)
                keyboard = get_inline_keyboard(
                buttons=rooms,
                width=1 if len(rooms) <= 7 else 2,
                util_buttons=[
                    ButtonLabel.BACK.value,
                    ButtonLabel.CANCEL.value,
                    ],
                width_util=2)
                
                await query.message.edit_text(
                    text=f"Selected date: {date}. Now select room.",
                    reply_markup=keyboard)
                await query.answer()
                await state.update_data(date=date)
                await state.set_state(FSMBooking.select_room)
    
    except Exception as e:
        await query.message.edit_text(text=f"Error: {e}")
        await state.clear()
        await query.answer()


#* Process Back button
@user_router.callback_query(
    F.data == ButtonLabel.BACK.value,
    StateFilter(
        FSMBooking.select_room,
        FSMBooking.select_desk))
async def process_back_button(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    config: Config):
    current_state = await state.get_state()
    
    if current_state == FSMBooking.select_room.state:
        # Get the config data
        c = config.bot_operation
        # Generate dates
        dates: List[str] = await generate_dates(
            c.num_days,
            c.exclude_weekends,
            c.timezone,
            c.country_code,
            c.date_format)
        
        keyboard = get_inline_keyboard(
            buttons=dates,
            width=1,
            util_buttons=[
                ButtonLabel.CANCEL.value,],
            width_util=1)

        await query.message.edit_text(
            text='Select date',
            reply_markup=keyboard)
        await query.answer()
        
        await state.set_state(FSMBooking.select_date)
        
    elif current_state == FSMBooking.select_desk.state:
        data = await state.get_data()
        date = data['date']
        rooms = await generate_available_rooms_list(session)
        keyboard = get_inline_keyboard(
        buttons=rooms,
        width=1 if len(rooms) <= 7 else 2,
        util_buttons=[
            ButtonLabel.BACK.value,
            ButtonLabel.CANCEL.value,
            ],
        width_util=2)
        
        await query.message.edit_text(
            text=f"Selected date: {date}. Now select room.",
            reply_markup=keyboard)
        await query.answer()
    
        await state.set_state(FSMBooking.select_room)
    
    else:
        await query.message.edit_text("Error: Invalid state")
        await state.clear()
        await query.answer()


#* Process room button
@user_router.callback_query(StateFilter(FSMBooking.select_room))
async def process_room_button(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    config: Config,
    ):
    data = await state.get_data()
    advanced_mode = data['advanced_mode']
    date = data['date']
    telegram_id = query.from_user.id
    date_format = str(config.bot_operation.date_format)
    room_name = str(query.data)
    await state.update_data(room_name=room_name)
    room_plan_url = await get_room_plan_by_room_name(session, room_name)
    
    # Retrive desks info: list[str], if there are desks, or empty list if there are no desks to book or str if there is an error message
    try:
        standard_access_days = config.bot_advanced_mode.standard_access_days if advanced_mode else None
        desks = await generate_desks_list(
            session,
            room_name,
            date,
            date_format,
            advanced_mode,
            telegram_id,
            standard_access_days)
        logger.info(f">>>>>>>>>>>>>desks (handler): {desks}")
        
    except Exception as e:
        await query.message.edit_text(text="An error occurred while retrieving available desks. Please try again later.")
        await state.clear()
        await query.answer()
        return
    
    # Generate keyboard with desks if desks is a list with strings, or send message that there are no desks available if desks is an empty list or send error message if desks is a string
    try:
        # Check if desks is a string (error message) or if it is an empty list
        if isinstance(desks, str):
            await query.message.edit_text(text=f"{desks}")
            await state.clear()
            await query.answer()
        elif not desks:
            await query.message.edit_text(text=f"No available desks in room: {room_name} for: {date}")
            await state.clear()
            await query.answer()
        else:
            keyboard = get_inline_keyboard(
            buttons=desks,
            width=1 if len(desks) <= 7 else 2,
            util_buttons=[
                ButtonLabel.BACK.value,
                ButtonLabel.CANCEL.value,
                ],
            width_util=2)
            
            await query.message.edit_text(
                text=f"Selected date: {date}, room: {room_name}. Now select desk according to <a href='{room_plan_url}'>room plan</a>.",
                reply_markup=keyboard)
            
            await state.set_state(FSMBooking.select_desk)
    
    except Exception as e:
        await query.message.edit_text(text=f"Error: {e}")
        await state.clear()
        await query.answer()


#* Process desk button
@user_router.callback_query(StateFilter(FSMBooking.select_desk))
async def process_desk_button(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    config: Config
    ):
    data = await state.get_data()
    telegram_id = query.from_user.id
    desk_name = str(query.data)
    room_name = str(data['room_name'])
    date = data['date']
    date_format = str(config.bot_operation.date_format)
    
    try:
        result = await desk_booker(
            session,
            telegram_id,
            desk_name,
            room_name,
            date,
            date_format,
        )
        await query.message.edit_text(f"{result}")
        await query.answer()
        await state.clear()
    except Exception as e:
        await query.message.edit_text(f"Error: {e}")
        await query.answer()
        await state.clear()