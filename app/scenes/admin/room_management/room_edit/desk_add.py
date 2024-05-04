from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.admin.desk_add import InputError, desk_add_service
from app.misc.const.button_labels import ButtonLabel
from app.keyboards.reply import get_reply_keyboard


class DeskAddScene(Scene, state="desk_add_scene"):


    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:       
        keyboard = get_reply_keyboard(
            util_buttons=[
                ButtonLabel.TO_MAIN_MENU.value,
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=3,
            one_time_keyboard=True,
            input_field_placeholder='Enter desk name, for example: "23450" or "A1"')

        await message.answer(
            text='Enter desk name',
            reply_markup=keyboard)


    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Desk Add Menu",
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
        try:
            result_message = await desk_add_service(session, room_name, desk_name=message.text)
            await message.answer(result_message)
            await self.wizard.retake()
        except InputError as e:
            await message.answer(str(e))
            await self.wizard.retake()
        except Exception as e:
            await message.answer(f'Failed to add desk: {str(e)}')
            await self.wizard.retake()