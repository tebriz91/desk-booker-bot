from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_kb import create_inline_kb

inline_router = Router()

@inline_router.message(Command('book'))
async def process_command_1(message: Message, session: AsyncSession):
    
    keyboard = create_inline_kb(1, last_btn='Cancel') # Customize the width of the keyboard and the buttons
            
    await message.answer(
        text='This is a custom inline keyboard. You can use it in your bot by importing the function <code>create_inline_kb</code>',
        reply_markup=keyboard
    )
