from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession

from misc.const.button_labels import ButtonLabel

from database.orm_queries import orm_select_users_from_waitlist
from keyboards.reply import create_reply_kb

class WaitlistScene(Scene, state="waitlist_scene"):
    
    @on.message.enter()
    async def on_enter(self, message: Message, session: AsyncSession) -> Any:
        waitlist_users_obj = await orm_select_users_from_waitlist(session) # TODO: Move this logic to a service
        waitlist_users = [waitlist_users.telegram_name for waitlist_users in waitlist_users_obj]
        keyboard = create_reply_kb(
            buttons= waitlist_users,
            width=4 if len(waitlist_users) > 7 else 3,
            util_buttons=[
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=2,
            one_time_keyboard=True)

        await message.answer(
            text="Waitlist Menu",
            reply_markup=keyboard)
    
    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Waitlist Menu",
            reply_markup=ReplyKeyboardRemove())
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.clear_data()
        await self.wizard.exit()

    @on.message(F.text == ButtonLabel.BACK.value)
    async def back(self, message: Message):
        await message.delete()
        await self.wizard.clear_data()
        await self.wizard.back()
    
    #* GOTO other scenes handlers
    @on.message(F.text)
    async def process_waitlist_username_button(self, message: Message, session: AsyncSession):
        await message.delete()
        await self.wizard.update_data(telegram_name=message.text)
        await self.wizard.goto("waitlist_user_info_scene", session=session)