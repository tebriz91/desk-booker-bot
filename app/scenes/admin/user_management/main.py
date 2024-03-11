from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

<<<<<<< HEAD
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, on

from misc.const.admin_menu import UserManagementMenu
from misc.const.button_labels import ButtonLabel
from keyboards.reply import create_reply_kb

class UserManagementScene(Scene, state="user_management"):
    
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        keyboard = create_reply_kb(
            buttons=[
                UserManagementMenu.ADD_USER.value,
                UserManagementMenu.DELETE_USER.value,
                UserManagementMenu.EDIT_USER.value,
                UserManagementMenu.BAN_USER.value,
                UserManagementMenu.UNBAN_USER.value,
                UserManagementMenu.BROWSE_USERS.value],
            width=3,
            util_buttons=[
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=2,
            one_time_keyboard=True)
        
        await message.answer(
            text="User Management Menu",
            reply_markup=keyboard)
=======
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
>>>>>>> 9ead955e717c190c7a83d0e1aa1f4102a4929b44
    
    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext) -> None:
        await message.delete()
        await message.answer(
            text="You've exited User Management Menu",
            reply_markup=ReplyKeyboardRemove())
    
<<<<<<< HEAD
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.exit()
    
    @on.message(F.text == ButtonLabel.BACK.value)
=======
    @on.message(F.text == "Exit")
    async def exit(self, message: Message):
        await self.wizard.exit()
    
    @on.message(F.text == "Back")
>>>>>>> 9ead955e717c190c7a83d0e1aa1f4102a4929b44
    async def back(self, message: Message):
        await message.delete()
        await self.wizard.back()
    
    #* GOTO other scenes handlers
<<<<<<< HEAD
    @on.message(F.text == UserManagementMenu.ADD_USER.value)
    async def to_user_add(self, message: Message):
        await message.delete()
        await self.wizard.goto("user_add")

    @on.message(F.text == UserManagementMenu.DELETE_USER.value)
    async def to_user_add(self, message: Message):
        await message.delete()
        await self.wizard.goto("user_delete")
=======
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
>>>>>>> 9ead955e717c190c7a83d0e1aa1f4102a4929b44
