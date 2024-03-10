from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession

from services.admin.add_user import UserInputError, add_user_service

class UserManagementScene(Scene, state="user_management"):
    
    #* The scene's entry point is designed to handle callback queries.
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        # Create reply keyboard
        keyboard = ReplyKeyboardBuilder()
        keyboard.button(text="Add User")
        keyboard.button(text="Delete User")
        keyboard.button(text="Ban User")
        keyboard.button(text="Unban User")
        keyboard.button(text="Edit User")
        keyboard.button(text="Show All Users")
        keyboard.button(text="Back")
        keyboard.button(text="Exit")

        await message.answer(
            text="User Management Menu",
            reply_markup=keyboard.adjust(2).as_markup(resize_keyboard=True))
    
    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext) -> None:
        await message.delete()
        await message.answer(
            text="You've exited User Management Menu",
            reply_markup=ReplyKeyboardRemove())
    
    @on.message(F.text == "Exit")
    async def exit(self, message: Message):
        await self.wizard.exit()
    
    @on.message(F.text == "Back")
    async def back(self, message: Message):
        await message.delete()
        await self.wizard.back()
    
    #* GOTO other scenes handlers
    # ...
    
    #* Add User handler
    @on.message(F.text == "Add User")
    async def add_user(self, message: Message):        
        await message.delete()

        # Create reply keyboard
        keyboard = ReplyKeyboardBuilder()
        keyboard.button(text="Back")
        keyboard.button(text="Exit")

        await message.answer(
            text="Enter telegram ID and telegram username",
            reply_markup=keyboard.adjust(2).as_markup(
                resize_keyboard=True,
                input_field_placeholder="123456789 @username"))
    
    # Handler to process the user's input
    @on.message(F.text)
    async def process_user_input(self, message: Message, state: FSMContext, session: AsyncSession):
        try:
            result_message = await add_user_service(session, message.text.strip())
            await message.answer(result_message)
            await self.wizard.retake()
        except UserInputError as e:
            await message.answer(str(e))
        except Exception as e:
            await message.answer(f"Failed to add user: {str(e)}")