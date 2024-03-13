from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession

from services.admin.room_delete import room_delete_service
from misc.const.button_labels import ButtonLabel
from keyboards.reply import create_reply_kb

class RoomDeleteScene(Scene, state="room_delete_scene"):
    
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        keyboard = create_reply_kb(
            util_buttons=[
                ButtonLabel.CONFIRM.value,
                ButtonLabel.CANCEL.value,
                ButtonLabel.EXIT.value],
            width_util=2,
            one_time_keyboard=True)

        await message.answer(
            text="Are you sure you want to delete the room?\nDeleting the room will also delete all associated desks and bookings.",
            reply_markup=keyboard)
    
    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Room Delete Menu",
            reply_markup=ReplyKeyboardRemove())
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.exit()

    #* Back to SelectRoomScene
    @on.message(F.text == ButtonLabel.CANCEL.value)
    async def cancel(self, message: Message, session: AsyncSession):
        await message.delete()
        # RoomSelectScene.on_enter() requires database session
        await self.wizard.back(session=session)

    @on.message(F.text == ButtonLabel.CONFIRM.value)
    async def confirm(self, message: Message, session: AsyncSession):
        data = await self.wizard.get_data()
        room_name = data.get('room_name')
        try:
            result_message = await room_delete_service(session, room_name)
            await message.answer(result_message)
            await self.wizard.back(session=session) #FIX: Change  to goto() method
        except Exception as e:
            await message.answer(f"An error occurred: {e}")
            await self.wizard.back(session=session)