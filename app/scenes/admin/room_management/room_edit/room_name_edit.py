from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession
from services.admin.room_name_edit import InputError, room_name_edit_service

from misc.const.button_labels import ButtonLabel
from keyboards.reply import create_reply_kb

class RoomNameEditScene(Scene, state="room_name_edit_scene"):

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

        data = await self.wizard.get_data()
        room_name = data.get('room_name')
        await message.answer(
            text=f'Enter a new room name for the room: {room_name}',
            reply_markup=keyboard)

    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Room Name Edit Menu",
            reply_markup=ReplyKeyboardRemove())
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.exit()
    
    @on.message(F.text == ButtonLabel.BACK.value)
    async def back(self, message: Message):
        await message.delete()
        await self.wizard.back()

    @on.message(F.text == ButtonLabel.TO_MAIN_MENU.value)
    async def to_main_menu(self, message: Message):
        await message.delete()
        await self.wizard.clear_data()
        await self.wizard.goto("admin_menu")
    
    @on.message(F.text)
    async def process_input(self, message: Message, session: AsyncSession):
        data = await self.wizard.get_data()
        old_room_name = data.get('room_name')
        new_room_name=message.text
        try:
            result_message = await room_name_edit_service(
                session,
                old_room_name,
                new_room_name)
            await message.answer(result_message)
            await self.wizard.update_data(room_name=new_room_name)
            await self.wizard.goto('room_edit_scene')
        except InputError as e:
            await message.answer(str(e))
            await self.wizard.retake()
        except Exception as e:
            await message.answer(f'Error: {str(e)}')
            await self.wizard.retake()