from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession

from misc.const.admin_menu import RoomManagementMenu, RoomEditMenu
from misc.const.button_labels import ButtonLabel
from keyboards.reply import create_reply_kb

class RoomEditScene(Scene, state="room_edit_scene"):
    
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        keyboard = create_reply_kb(
            buttons=[
                RoomEditMenu.EDIT_ROOM_NAME.value,
                RoomEditMenu.TOGGLE_AVAILABILITY.value,
                RoomEditMenu.EDIT_ROOM_PLAN.value,
                RoomEditMenu.EDIT_ADDITIONAL_INFO.value],
            width=2,
            util_buttons=[
                ButtonLabel.TO_MAIN_MENU.value,
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=3,
            one_time_keyboard=True)

        await message.answer(
            text="Room Edit Menu",
            reply_markup=keyboard)
    
    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Room Edit Menu",
            reply_markup=ReplyKeyboardRemove())
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.exit()

    #* Back to SelectRoomScene
    @on.message(F.text == ButtonLabel.BACK.value)
    async def back(self, message: Message, session: AsyncSession):
        await message.delete()
        # RoomSelectScene.on_enter() requires database session
        await self.wizard.back(session=session)

    @on.message(F.text == ButtonLabel.TO_MAIN_MENU.value)
    async def to_main_menu(self, message: Message):
        await message.delete()
        await self.wizard.clear_data()
        await self.wizard.goto("admin_menu")
    
    #* GOTO other scenes handlers
    @on.message(F.text == RoomEditMenu.EDIT_ROOM_NAME.value)
    async def to_room_name_edit(self, message: Message):
        await message.delete()
        await self.wizard.goto("room_name_edit_scene")
    
    @on.message(F.text == RoomEditMenu.TOGGLE_AVAILABILITY.value)
    async def to_room_availability_toggle(self, message: Message):
        await message.delete()
        await self.wizard.goto("room_availability_toggle_scene")
        
    @on.message(F.text == RoomEditMenu.EDIT_ROOM_PLAN.value)
    async def to_room_plan_edit(self, message: Message):
        await message.delete()
        await message.answer("Not implemented yet")
        # await self.wizard.goto("room_plan_edit_scene")
    
    @on.message(F.text == RoomEditMenu.EDIT_ADDITIONAL_INFO.value)
    async def to_room_additional_info_edit(self, message: Message):
        await message.delete()
        await message.answer("Not implemented yet")
        await self.wizard.retake()
        # await self.wizard.goto("room_additional_info_edit_scene")