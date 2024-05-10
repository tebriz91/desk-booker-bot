from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.admin.waitlist_user_info import waitlist_user_info_service
from app.services.admin.user_add import user_add_service_by_telegram_name_from_wl
from app.services.admin.waitlist_user_delete import waitlist_user_delete_by_username_service
from app.misc.const.button_labels import ButtonLabel
from app.keyboards.reply import get_reply_keyboard


class WaitlistUserInfoScene(Scene, state="waitlist_user_info_scene"):
    
    
    @on.message.enter()
    async def on_enter(self, message: Message, session: AsyncSession) -> Any:
        data = await self.wizard.get_data()
        telegram_name = data.get('telegram_name')
        try:
            user_info = await waitlist_user_info_service(session, telegram_name)
        except Exception as e:
            user_info = f"Error: {e}"
        
        keyboard = get_reply_keyboard(
            buttons=[
                ButtonLabel.YES.value,
                ButtonLabel.NO.value],
            width=2,
            util_buttons=[
                ButtonLabel.TO_MAIN_MENU.value,
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=3,
            one_time_keyboard=True)

        await message.answer(
            text=f"{user_info}",
            reply_markup=keyboard)


    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Waitlist User Info Menu",
            reply_markup=ReplyKeyboardRemove())
    
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.clear_data()
        await self.wizard.exit()


    @on.message(F.text == ButtonLabel.TO_MAIN_MENU.value)
    async def to_main_menu(self, message: Message):
        await message.delete()
        await self.wizard.clear_data()
        await self.wizard.goto("admin_menu")


    @on.message(F.text == ButtonLabel.BACK.value)
    async def back(self, message: Message, session: AsyncSession):
        await message.delete()
        await self.wizard.clear_data()
        # WaitlistScene.on_enter() requires database session
        await self.wizard.back(session=session)


    @on.message(F.text == ButtonLabel.YES.value)
    async def process_yes_button(self, message: Message, session: AsyncSession):
        await message.delete()
        data = await self.wizard.get_data()
        telegram_name = data.get('telegram_name')
        try:
            result_message = await user_add_service_by_telegram_name_from_wl(session, telegram_name)
            await message.answer(result_message)
            await waitlist_user_delete_by_username_service (session, telegram_name)
            await self.wizard.clear_data()
            await self.wizard.back(session=session)
        except Exception as e:
            await message.answer(f"Failed to add user: {str(e)}")
            await self.wizard.clear_data()
            await self.wizard.back(session=session)


    @on.message(F.text == ButtonLabel.NO.value)
    async def process_no_button(self, message: Message, session: AsyncSession):
        await message.delete()
        data = await self.wizard.get_data()
        telegram_name = data.get('telegram_name')
        try:
            result_message = await waitlist_user_delete_by_username_service(session, telegram_name)
            await message.answer(f"{result_message}")
            await self.wizard.clear_data()
            await self.wizard.back(session=session)
        except Exception as e:
            await message.answer(f"Failed to delete user: {str(e)}")
            await self.wizard.clear_data()
            await self.wizard.back(session=session)