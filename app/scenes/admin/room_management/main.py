from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession

from misc.const.admin_menu import RoomManagementMenu
from misc.const.button_labels import ButtonLabel
from keyboards.reply import create_reply_kb

class RoomManagementScene(Scene, state="room_management_scene"):
    
    @on.message.enter()
    async def on_enter(self, message: Message, flag: RoomManagementMenu = None) -> Any:
        """
        flag: Scene argument, can be passed to the scene using the wizard. It is stored in state data and can be used in other scenes to determine the action that the user wants to perform.
        """
        keyboard = create_reply_kb(
            buttons=[
                RoomManagementMenu.ADD_ROOM.value,
                RoomManagementMenu.DELETE_ROOM.value,
                RoomManagementMenu.EDIT_ROOM.value,
                RoomManagementMenu.BROWSE_ROOMS.value],
            width=2,
            util_buttons=[
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=2,
            one_time_keyboard=True)

        await message.answer(
            text="Room Management Menu",
            reply_markup=keyboard)
    
    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Room Management Menu",
            reply_markup=ReplyKeyboardRemove())
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.exit()

    @on.message(F.text == ButtonLabel.BACK.value)
    async def back(self, message: Message):
        await message.delete()
        await self.wizard.back()

    #* GOTO other scenes handlers
    @on.message(F.text == RoomManagementMenu.ADD_ROOM.value)
    async def to_room_add(self, message: Message):
        await message.delete()
        await self.wizard.goto("room_add_scene")
    
    #* GOTO RoomSelectScene scenes handlers
    @on.message(F.text == RoomManagementMenu.DELETE_ROOM.value)
    async def to_room_delete(self, message: Message, session: AsyncSession):
        await message.delete()
        await self.wizard.update_data(flag=RoomManagementMenu.DELETE_ROOM.value)
        # RoomSelectScene.on_enter() requires database session
        await self.wizard.goto("room_select_scene", session=session)
        
    @on.message(F.text == RoomManagementMenu.EDIT_ROOM.value)
    async def to_room_edit(self, message: Message, session: AsyncSession):
        await message.delete()
        await self.wizard.update_data(flag=RoomManagementMenu.EDIT_ROOM.value)
        await self.wizard.goto("room_select_scene", session=session)
    
    @on.message(F.text == RoomManagementMenu.BROWSE_ROOMS.value)
    async def to_room_browse(self, message: Message, session: AsyncSession):
        await message.delete()
        await self.wizard.update_data(flag=RoomManagementMenu.BROWSE_ROOMS.value)
        await self.wizard.goto("room_select_scene", session=session)