from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_select_rooms

from keyboards.inline_kb import create_inline_kb, create_inline_kb_2

inline_router = Router()

@inline_router.message(Command('book'))
async def process_command_1(
    message: Message,
    session: AsyncSession,
    num_days: int, # Number of days to generate (env variable that transfered through dp.workflow_data)
    exclude_weekends: bool,
    timezone: str,
    country_code: str
    ):
    
    # Create an inline keyboard with the function create_inline_kb with the following parameters:
    keyboard = create_inline_kb(
        num_days,
        exclude_weekends,
        timezone,
        country_code,
        1, # Width of the keyboard
        last_btn='Cancel'
        )

    await message.answer(
        text='Choose a date:',
        reply_markup=keyboard
    )

# Process the last button (Cancel)
@inline_router.callback_query(F.data == "last_btn")
async def process_callback_query_1(query: CallbackQuery):
    await query.message.edit_text("Process has been canceled")
    await query.answer()

# Process the date button
@inline_router.callback_query()
async def process_callback_query_2(
    query: CallbackQuery,
    session: AsyncSession
    ):
    rooms_orm_obj = await orm_select_rooms(session)
    rooms = [rooms.name for rooms in rooms_orm_obj]
        
    keyboard = create_inline_kb_2(rooms, 1, last_btn='Cancel')

    await query.message.edit_text(
    text='Choose a room:',
    reply_markup=keyboard
    )