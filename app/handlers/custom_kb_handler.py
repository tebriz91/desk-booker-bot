from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.custom_inline_kb import create_inline_kb, create_inline_kb_2
from lexicon.lexicon_buttons import BUTTONS

kb_router = Router()

@kb_router.message(Command('book2'))
async def process_command_1(message: Message, session: AsyncSession):
    
    keyboard = create_inline_kb(4, last_btn='Cancel', **BUTTONS) # Customize the width of the keyboard and the buttons
            
    await message.answer(
        text='This is a custom inline keyboard. You can use it in your bot by importing the function <code>create_inline_kb</code>',
        reply_markup=keyboard
    )

# Process the buttons
@kb_router.callback_query(F.data.in_(list(BUTTONS))) # list(BUTTONS) is a list of all keys from the dictionary BUTTONS
async def process_callback_query_1(query: CallbackQuery):
    
    keyboard = create_inline_kb_2(4, last_btn='Cancel', **BUTTONS)
    
    await query.message.edit_text(
        text=f"You have pressed the button {BUTTONS[query.data]}",
        reply_markup=keyboard
    )
    await query.answer()

# Process the last button (Cancel)
@kb_router.callback_query(F.data == "last_btn")
async def process_callback_query_2(query: CallbackQuery):
    await query.message.edit_text("Process has been canceled")
    await query.answer()