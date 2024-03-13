from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession
from services.admin.room_add import InputError, room_add_service

from misc.const.button_labels import ButtonLabel
from keyboards.reply import create_reply_kb

class RoomAddScene(Scene, state="room_add_scene"):

    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:       
        keyboard = create_reply_kb(
            util_buttons=[
                ButtonLabel.TO_MAIN_MENU.value,
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=3,
            one_time_keyboard=True,
            input_field_placeholder='Enter room name, for example: "108" or "A"')

        await message.answer(
            text='Enter room name',
            reply_markup=keyboard)

    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited User Add Menu",
            reply_markup=ReplyKeyboardRemove())
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.exit()
    
    @on.message(F.text == ButtonLabel.BACK.value)
    async def back(self, message: Message):
        await message.delete()
        await self.wizard.clear_data()
        await self.wizard.back()

    @on.message(F.text == ButtonLabel.TO_MAIN_MENU.value)
    async def to_main_menu(self, message: Message):
        await message.delete()
        await self.wizard.clear_data()
        await self.wizard.goto("admin_menu")
    
    @on.message(F.text)
    async def process_input(self, message: Message, session: AsyncSession):
        try:
            result_message = await room_add_service(session, room_name=message.text)
            await message.answer(result_message)
            await self.wizard.retake()
        except InputError as e:
            await message.answer(str(e))
            await self.wizard.retake()
        except Exception as e:
            await message.answer(f'Failed to add room: {str(e)}')
            await self.wizard.retake()