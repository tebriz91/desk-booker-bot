from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession
from services.admin.room_availability_toggle import room_availability_toggle_service

from misc.const.button_labels import ButtonLabel
from keyboards.reply import create_reply_kb

class RoomAvailabilityToggleScene(Scene, state="room_availability_toggle_scene"):

    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:       
        keyboard = create_reply_kb(
            util_buttons=[
                ButtonLabel.TOGGLE.value,
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=3,
            one_time_keyboard=True)

        data = await self.wizard.get_data()
        room_name = data.get('room_name')
        await message.answer(
            text=f'Press "Toggle" to change the availability of the room: {room_name}',
            reply_markup=keyboard)

    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Room Toggle Availability Menu",
            reply_markup=ReplyKeyboardRemove())
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.exit()
    
    @on.message(F.text == ButtonLabel.BACK.value)
    async def back(self, message: Message):
        await message.delete()
        await self.wizard.back()

    @on.message(F.text == ButtonLabel.TOGGLE.value)
    async def toggle_room_availability(self, message: Message, session: AsyncSession):
        await message.delete()
        data = await self.wizard.get_data()
        room_name = data.get('room_name')
        try:
            result_message = await room_availability_toggle_service(session, room_name)
            await message.answer(result_message)
            await self.wizard.retake()
        except Exception as e:
            await message.answer(f"An error occurred: {e}")
            await self.wizard.retake()