from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.admin.user_delete_by_id import UserInputError, user_delete_by_id_service
from app.misc.const.button_labels import ButtonLabel
from app.keyboards.reply import get_reply_keyboard


class UserDeleteByIDScene(Scene, state="user_delete_by_id_scene"):
    
    
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        keyboard = get_reply_keyboard(
            util_buttons=[
                ButtonLabel.TO_MAIN_MENU.value,
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=3,
            one_time_keyboard=True,
            input_field_placeholder="123456789")

        await message.answer(
            text="Enter telegram ID",
            reply_markup=keyboard)
    
    
    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited User Delete By ID Menu",
            reply_markup=ReplyKeyboardRemove())
    
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.clear_data()
        await self.wizard.exit()
    
    
    @on.message(F.text == ButtonLabel.BACK.value)
    async def back(self, message: Message):
        await message.delete()
        await self.wizard.back() # FIX: Change back() method to goto() if it's required


    @on.message(F.text == ButtonLabel.TO_MAIN_MENU.value)
    async def to_main_menu(self, message: Message):
        await message.delete()
        await self.wizard.clear_data()
        await self.wizard.goto("admin_menu")
    
    
    # TODO: Ask for confirmation before deleting the user
    # Handler to process the user's input
    @on.message(F.text)
    async def process_user_input(
        self,
        message: Message,
        session: AsyncSession):
        try:
            result_message = await user_delete_by_id_service(session, message.text)
            await message.answer(result_message)
            await self.wizard.retake()
        except UserInputError as e:
            await message.answer(str(e))
            await self.wizard.retake()
        except Exception as e:
            await message.answer(f"Failed to delete user: {str(e)}")
            await self.wizard.retake()            