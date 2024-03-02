from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from sqlalchemy.ext.asyncio import AsyncSession

from enums.button_labels import ButtonLabel

from keyboards.callbacks import CBFAllBookings, CBFUtilButtons

from states.user import FSMAllBookings

from routers.user.router import user_router

from database.orm_queries import orm_select_room_id_by_name, orm_select_rooms

from keyboards.all_bookings_kb import create_kb_with_room_names
from keyboards.utils.callback_btns import get_inline_keyboard_with_util_buttons

from services.bookings_list_generator import generate_list_of_all_current_bookings_by_room_id

#* Process command /all_bookings
@user_router.message(
    Command("all_bookings"),
    StateFilter(default_state))
async def process_command_all_bookings_in_default_state(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    ):
    # Retrieve rooms from the database
    rooms_orm_obj = await orm_select_rooms(session)
    rooms = [rooms.name for rooms in rooms_orm_obj]
    # Create an inline keyboard with available room names as buttons
    if len(rooms) <= 7:
        keyboard = create_kb_with_room_names(
            rooms,
            width=1,
            util_buttons_order=['cancel'],
            util_buttons_width=2,
            cancel_btn=ButtonLabel.CANCEL.value)
    else:
        keyboard = create_kb_with_room_names(
            rooms,
            width=2,
            util_buttons_order=['cancel'],
            util_buttons_width=2,
            cancel_btn=ButtonLabel.CANCEL.value)

    await message.answer(
    text='Choose a room:',
    reply_markup=keyboard
    )
    
    await state.set_state(FSMAllBookings.select_room)

#* Process /all_bookings command in states other than default
@user_router.message(
    Command("all_bookings"),
    StateFilter(
        FSMAllBookings.select_room,
        FSMAllBookings.view_bookings))
async def process_command_all_bookings_in_all_bookings_states(message: Message):
    await message.answer(
        text="You are already in the process of viewing all bookings. Please, finish the process or cancel it."
    )

#* Process /all_bookings, if the user has another unfinished process
# Catch-all handler for the /all_bookings command in any state other than the default state
@user_router.message(
    Command("all_bookings"),
    ~StateFilter(default_state))
async def process_command_all_bookings_in_non_default_state(message: Message):
    await message.answer(
        text="You have to finish or cancel other current process before using this command."
    )

#* Process the button 'Cancel' in the select_room state
@user_router.callback_query(
    CBFUtilButtons.filter(
        F.action == ButtonLabel.CANCEL.value),
    StateFilter(FSMAllBookings.select_room))
async def process_cancel_button(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text("Process canceled")
    await query.answer()
    await state.clear()

#* Process the button 'Ok' in the view_bookings state
@user_router.callback_query(
    CBFUtilButtons.filter(
        F.action == ButtonLabel.OK.value),
    StateFilter(FSMAllBookings.view_bookings))
async def process_ok_button(query: CallbackQuery, state: FSMContext):
    # Remove inline keyboard from the message
    await query.message.edit_reply_markup(reply_markup=None)
    await query.message.answer("Process finished")
    await state.clear()

#* Process the room button
@user_router.callback_query(
    CBFAllBookings.filter(),
    StateFilter(FSMAllBookings.select_room))
async def process_room_button(
    query: CallbackQuery,
    callback_data: CBFAllBookings,
    state: FSMContext,
    session: AsyncSession,
    date_format: str,
    date_format_short: str) -> None:
    room_name = callback_data.room_name
    room_id = await orm_select_room_id_by_name(session, room_name)
    bookings = await generate_list_of_all_current_bookings_by_room_id(
        session,
        date_format,
        date_format_short,
        room_id)
    await query.message.edit_text(
        text=bookings,
        # Add keyboard with "Back" and "Ok" buttons
        reply_markup=get_inline_keyboard_with_util_buttons(
            button_order=['back', 'ok'],
            sizes=(2,),
            back_btn=ButtonLabel.BACK.value,
            ok_btn=ButtonLabel.OK.value
        ),)
    await state.set_state(FSMAllBookings.view_bookings)
    await query.answer()

#* Process the back button
@user_router.callback_query(
    CBFUtilButtons.filter(
        F.action == ButtonLabel.BACK.value),
    StateFilter(FSMAllBookings.view_bookings))
async def process_back_button(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession):
    await state.set_state(FSMAllBookings.select_room)
    # Retrieve rooms from the database
    rooms_orm_obj = await orm_select_rooms(session)
    rooms = [rooms.name for rooms in rooms_orm_obj]
    # Create an inline keyboard with available room names as buttons
    if len(rooms) <= 7:
        keyboard = create_kb_with_room_names(
            rooms,
            width=1,
            util_buttons_order=['cancel'],
            util_buttons_width=2,
            cancel_btn=ButtonLabel.CANCEL.value)
    else:
        keyboard = create_kb_with_room_names(
            rooms,
            width=2,
            util_buttons_order=['cancel'],
            util_buttons_width=2,
            cancel_btn=ButtonLabel.CANCEL.value)

    await query.message.edit_text(
    text='Choose a room:',
    reply_markup=keyboard
    )