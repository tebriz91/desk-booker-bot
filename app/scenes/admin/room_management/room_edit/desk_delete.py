from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.admin.desk_delete import desk_delete_service
from app.misc.const.button_labels import ButtonLabel
from app.keyboards.reply import get_reply_keyboard


class DeskDeleteScene(Scene, state="desk_delete_scene"):
    
    
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        keyboard = get_reply_keyboard(
            util_buttons=[
                ButtonLabel.CONFIRM.value,
                ButtonLabel.CANCEL.value,
                ButtonLabel.EXIT.value],
            width_util=2,
            one_time_keyboard=True)

        await message.answer(
            text="Are you sure you want to delete the desk?\nDeleting the desk will also delete all associated bookings.",
            reply_markup=keyboard)
    
    
    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Desk Delete Menu",
            reply_markup=ReplyKeyboardRemove())
    
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.exit()


    #* Back to SelectDeskScene
    @on.message(F.text == ButtonLabel.CANCEL.value)
    async def cancel(self, message: Message, session: AsyncSession):
        await message.delete()
        # DeskSelectScene.on_enter() requires database session
        await self.wizard.back(session=session)


    @on.message(F.text == ButtonLabel.CONFIRM.value)
    async def confirm_desk_deletion(self, message: Message, session: AsyncSession):
        await message.delete()
        data = await self.wizard.get_data()
        desk_name = data.get('desk_name')
        room_name = data.get('room_name')
        try:
            result_message = await desk_delete_service(session, desk_name, room_name)
            await message.answer(result_message)
            await self.wizard.back(session=session) # FIX: Change back() method to goto() if it's required
        except Exception as e:
            await message.answer(f"An error occurred: {e}")
            await self.wizard.back(session=session)