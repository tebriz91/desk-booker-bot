from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession
from services.admin.desk_name_edit import InputError, desk_name_edit_service

from misc.const.button_labels import ButtonLabel
from keyboards.reply import create_reply_kb

class DeskNameEditScene(Scene, state="desk_name_edit_scene"):

    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:       
        keyboard = create_reply_kb(
            util_buttons=[
                ButtonLabel.TO_MAIN_MENU.value,
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=3,
            one_time_keyboard=True,
            input_field_placeholder='Enter desk name, for example: "23450" or "A1"')

        data = await self.wizard.get_data()
        desk_name = data.get('desk_name')
        room_name = data.get('room_name')
        await message.answer(
            text=f'Enter a new desk name for desk: {desk_name} in room: {room_name}',
            reply_markup=keyboard)

    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Desk Name Edit Menu",
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
        room_name = data.get('room_name')
        old_desk_name = data.get('desk_name')
        new_desk_name = message.text
        try:
            result_message = await desk_name_edit_service(
                session,
                room_name,
                old_desk_name,
                new_desk_name)
            await message.answer(result_message)
            await self.wizard.update_data(desk_name=new_desk_name)
            await self.wizard.goto('desk_edit_scene') #TODO: Check if it is better to use back() method instead of goto()
        except InputError as e:
            await message.answer(str(e))
            await self.wizard.retake()
        except Exception as e:
            await message.answer(f'Error: {str(e)}')
            await self.wizard.retake()