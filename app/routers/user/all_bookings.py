from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from sqlalchemy.ext.asyncio import AsyncSession

from config_data.config import Config

from misc.const.button_labels import ButtonLabel

from states.user import FSMAllBookings

from routers.user.router import user_router

from database.orm_queries import orm_select_room_id_by_name

from keyboards.inline import get_inline_keyboard

from services.common.rooms_list_generator import generate_available_rooms_list
from services.bookings_list_generator import generate_list_of_all_current_bookings_by_room_id

from utils.logger import Logger

logger = Logger(__name__)


#* Process command /all_bookings
@user_router.message(
    Command("all_bookings"),
    StateFilter(default_state))
async def process_command_all_bookings_in_default_state(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    ):
    rooms = await generate_available_rooms_list(session)
    keyboard = get_inline_keyboard(
    buttons=rooms,
    width=1 if len(rooms) <= 7 else 2,
    util_buttons=[
        ButtonLabel.CANCEL.value,
        ],
    width_util=1)

    await message.answer(
    text='Select room',
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


#* Process cancel button
@user_router.callback_query(
    F.data == ButtonLabel.CANCEL.value,
    StateFilter(FSMAllBookings.select_room))
async def process_cancel_button(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text("Process canceled")
    await query.answer()
    await state.clear()


#* Process back button
@user_router.callback_query(
    F.data == ButtonLabel.BACK.value,
    StateFilter(FSMAllBookings.view_bookings))
async def process_back_button(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession):

    rooms = await generate_available_rooms_list(session)
    keyboard = get_inline_keyboard(
    buttons=rooms,
    width=1 if len(rooms) <= 7 else 2,
    util_buttons=[
        ButtonLabel.CANCEL.value,
        ],
    width_util=1)

    await query.message.edit_text(
    text='Select room',
    reply_markup=keyboard
    )
    await query.answer()
    await state.set_state(FSMAllBookings.select_room)


#* Process Ok button
@user_router.callback_query(
    F.data == ButtonLabel.OK.value,
    StateFilter(FSMAllBookings.view_bookings))
async def process_ok_button(query: CallbackQuery, state: FSMContext):
    # Remove inline keyboard from the message
    await query.message.edit_reply_markup(reply_markup=None)
    await query.message.answer("Process finished")
    await state.clear()


#* Process the room button
@user_router.callback_query(StateFilter(FSMAllBookings.select_room))
async def process_room_button(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    config: Config) -> None:
    date_format = str(config.bot_operation.date_format)
    date_format_short = str(config.bot_operation.date_format_short)
    room_name = query.data
    room_id = await orm_select_room_id_by_name(session, room_name)
    bookings = await generate_list_of_all_current_bookings_by_room_id(
        session,
        date_format,
        date_format_short,
        room_id)
    # Add keyboard with "Back" and "Ok" buttons
    logger.info(f">>>>>>>>>>>>>>> bookings: {bookings}")
    keyboard = get_inline_keyboard(
    util_buttons=[
        ButtonLabel.BACK.value,
        ButtonLabel.OK.value,
        ],
    width_util=2)
    
    logger.info(f">>>>>>>>>>>>>>> bookings: {bookings}")
    
    try:
        await query.message.edit_text(
            text=bookings,
            parse_mode='HTML',
            reply_markup=keyboard)
        await query.answer()
    except Exception as e:
        await query.message.edit_text(
            text=f"Error: {e}"
        )

    await state.set_state(FSMAllBookings.view_bookings)