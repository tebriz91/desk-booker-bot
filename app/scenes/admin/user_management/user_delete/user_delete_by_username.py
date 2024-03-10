from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession
from services.admin.user_delete_by_username import UserInputError, user_delete_by_username_service

from misc.const.button_labels import ButtonLabel
from keyboards.reply import create_reply_kb

class UserDeleteByUsernameScene(Scene, state="user_delete_by_username"):
    
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        keyboard = create_reply_kb(
            util_buttons=[
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=2,
            one_time_keyboard=True,
            input_field_placeholder="@username")

        await message.answer(
            text="Enter telegram username",
            reply_markup=keyboard)
    
    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext) -> None:
        await message.delete()
        await message.answer(
            text="You've exited User Delete By Username Menu",
            reply_markup=ReplyKeyboardRemove())
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.exit()
    
    @on.message(F.text == ButtonLabel.BACK.value)
    async def back(self, message: Message):
        await message.delete()
        await self.wizard.back()

    # BUG: When pressing the back button after successfully deleting a user, the scene retakes again and asks for the username
    # TODO: Ask for confirmation before deleting the user
    # Handler to process the user's input
    @on.message(F.text)
    async def process_user_input(
        self,
        message: Message,
        state: FSMContext,
        session: AsyncSession):
        try:
            result_message = await user_delete_by_username_service(session, message.text)
            await message.answer(result_message)
            await self.wizard.retake()
        except UserInputError as e:
            await message.answer(str(e))
        except Exception as e:
            await message.answer(f"Failed to delete user: {str(e)}")