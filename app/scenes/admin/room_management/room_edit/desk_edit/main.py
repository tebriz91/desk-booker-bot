from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession

from misc.const.admin_menu import DeskEditMenu
from misc.const.button_labels import ButtonLabel
from keyboards.reply import create_reply_kb

class DeskEditScene(Scene, state="desk_edit_scene"):
    
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        keyboard = create_reply_kb(
            buttons=[
                DeskEditMenu.EDIT_DESK_NAME.value,
                DeskEditMenu.TOGGLE_AVAILABILITY.value],
            width=3,
            util_buttons=[
                ButtonLabel.TO_MAIN_MENU.value,
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=3,
            one_time_keyboard=True)

        await message.answer(
            text="Desk Edit Menu",
            reply_markup=keyboard)
    
    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Desk Edit Menu",
            reply_markup=ReplyKeyboardRemove())
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.exit()

    #* Back to SelectDeskScene
    @on.message(F.text == ButtonLabel.BACK.value)
    async def back(self, message: Message, session: AsyncSession):
        await message.delete()
        # DeskSelectScene.on_enter() requires database session
        await self.wizard.back(session=session)

    @on.message(F.text == ButtonLabel.TO_MAIN_MENU.value)
    async def to_main_menu(self, message: Message):
        await message.delete()
        await self.wizard.clear_data()
        await self.wizard.goto("admin_menu")
    
    #* GOTO other scenes handlers
    @on.message(F.text == DeskEditMenu.EDIT_DESK_NAME.value)
    async def to_desk_name_edit(self, message: Message):
        await message.delete()
        await self.wizard.goto("desk_name_edit_scene")
    
    @on.message(F.text == DeskEditMenu.TOGGLE_AVAILABILITY.value)
    async def to_desk_availability_toggle(self, message: Message):
        await message.delete()
        await self.wizard.goto("desk_availability_toggle_scene")