from aiogram import F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from sqlalchemy.ext.asyncio import AsyncSession

from config_data.config import Config

from services.bookings_list_generator import (
    generate_dict_of_current_bookings_by_telegram_id_for_inline_kb,
    generate_list_of_current_bookings_by_telegram_id)

from keyboards.utils.callback_btns import get_inline_keyboard_with_util_buttons

from misc.const.button_labels import ButtonLabel

from keyboards.callbacks import CBFCancelBooking, CBFUtilButtons

from states.user import FSMCancelBooking

from routers.user.router import user_router

from keyboards.cancel_bookings_kb import create_kb_with_bookings_to_cancel

from database.orm_queries import orm_delete_booking_by_id

#* Process command /cancel_bookings in default state
@user_router.message(Command('cancel_bookings'), StateFilter(default_state))
async def process_cancel_bookings_command(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    config: Config) -> None:
    date_format = config.bot_operation.date_format
    telegram_id = message.from_user.id   
    bookings = await generate_dict_of_current_bookings_by_telegram_id_for_inline_kb(
        session,
        date_format,
        telegram_id)
    
    if not bookings:
        await message.answer(text="You have no bookings to cancel")
        await state.clear()
    else:
        keyboard = create_kb_with_bookings_to_cancel(
            bookings,
            width=1,
            util_buttons_order=['cancel'],
            util_buttons_width=1,
            cancel_btn=ButtonLabel.CANCEL.value)
        
        await message.answer(
            text="Choose a booking to cancel:",
            reply_markup=keyboard)
        
        await state.set_state(FSMCancelBooking.select_booking)

#* Process command /cancel_bookings in states other than default
@user_router.message(
    Command('cancel_bookings'),
    StateFilter(FSMCancelBooking.select_booking,
                FSMCancelBooking.view_bookings))
async def process_cancel_bookings_command_in_other_states(
    message: Message) -> None:
    await message.answer(
        text="You are already in the process of cancelling a booking. Please finish the process or cancel it.")

#* Process button /cancel_bookings if the user has another unfinished process
@user_router.message(
    Command('cancel_bookings'),
    ~StateFilter(default_state))
async def process_cancel_bookings_command_in_non_default_state(
    message: Message) -> None:
    await message.answer(
        text="You have to finish or cancel other current process before using this command.")

#* Process button 'Cancel' in the select_booking state
@user_router.callback_query(
    CBFUtilButtons.filter(
        F.action == ButtonLabel.CANCEL.value),
    StateFilter(FSMCancelBooking.select_booking))
async def process_cancel_button_in_select_booking_state(
    query: CallbackQuery,
    state: FSMContext) -> None:
    await query.message.edit_text(
        text="Process canceled")
    await query.answer()
    await state.clear()

#* Process button 'Ok' in the view_bookings state
@user_router.callback_query(
    CBFUtilButtons.filter(
        F.action == ButtonLabel.OK.value),
    StateFilter(FSMCancelBooking.view_bookings))
async def process_ok_button_in_view_bookings_state(
    query: CallbackQuery,
    state: FSMContext) -> None:
    await query.message.edit_reply_markup(reply_markup=None)
    await query.message.answer(text="Process finished")
    await state.clear()

#* Process button with booking to cancel
@user_router.callback_query(
    CBFCancelBooking.filter(),
    StateFilter(FSMCancelBooking.select_booking))
async def process_button_with_booking_to_cancel(
    query: CallbackQuery,
    callback_data: CBFCancelBooking,
    state: FSMContext,
    session: AsyncSession,
    config: Config) -> None:
    date_format = config.bot_operation.date_format
    date_format_short = config.bot_operation.date_format_short
    telegram_id = query.from_user.id
    telegram_name = query.from_user.username
    booking_id = callback_data.booking_id
    await orm_delete_booking_by_id (session, booking_id)
    updated_bookings = await generate_list_of_current_bookings_by_telegram_id(
        session,
        date_format,
        date_format_short,
        telegram_id,
        telegram_name)
    await query.message.edit_text(
        text=f'Booking canceled.\n\n{updated_bookings}',
        reply_markup=get_inline_keyboard_with_util_buttons(
            button_order=['back', 'ok'],
            sizes=(2,),
            back_btn=ButtonLabel.BACK.value,
            ok_btn=ButtonLabel.OK.value
        ),)
    await state.set_state(FSMCancelBooking.view_bookings)
    await query.answer()
    
#* Process button 'Back' in the view_bookings state
@user_router.callback_query(
    CBFUtilButtons.filter(
        F.action == ButtonLabel.BACK.value),
    StateFilter(FSMCancelBooking.view_bookings))
async def process_back_button_in_view_bookings_state(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    config: Config) -> None:
    date_format = config.bot_operation.date_format
    telegram_id = query.from_user.id
    bookings = await generate_dict_of_current_bookings_by_telegram_id_for_inline_kb(
        session,
        date_format,
        telegram_id)
    
    if not bookings:
        await query.message.edit_text(text="You have no bookings to cancel")
        await state.clear()
    else:
        keyboard = create_kb_with_bookings_to_cancel(
            bookings,
            width=1,
            util_buttons_order=['cancel'],
            util_buttons_width=1,
            cancel_btn=ButtonLabel.CANCEL.value)
        
        await query.message.edit_text(
            text="Choose a booking to cancel:",
            reply_markup=keyboard)
        
        await query.answer()
        await state.set_state(FSMCancelBooking.select_booking)