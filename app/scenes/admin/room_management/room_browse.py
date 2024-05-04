from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.admin.room_browse import room_browse_service
from app.misc.const.admin_menu import RoomManagementMenu
from app.misc.const.button_labels import ButtonLabel
from app.keyboards.reply import get_reply_keyboard


class RoomBrowseScene(Scene, state="room_browse_scene"):
    
    
    @on.message.enter()
    async def on_enter(self, message: Message, session: AsyncSession) -> Any:
        """
        Do not forget to pass session to the on_enter()
        """
        data = await self.wizard.get_data()
        room_name = data.get('room_name')
        try:
            result_message = await room_browse_service(session, room_name)
        except Exception as e:
            result_message = f"Error: {e}"
        
        keyboard = get_reply_keyboard(
            buttons=[
                RoomManagementMenu.EDIT_ROOM.value],
            width=1,
            util_buttons=[
                ButtonLabel.TO_MAIN_MENU.value,
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=3,
            one_time_keyboard=True)

        await message.answer(
            text=f"{result_message}",
            reply_markup=keyboard)
    
    
    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Room Browse Menu",
            reply_markup=ReplyKeyboardRemove())
    
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.exit()


    @on.message(F.text == ButtonLabel.TO_MAIN_MENU.value)
    async def to_main_menu(self, message: Message):
        await message.delete()
        await self.wizard.clear_data()
        await self.wizard.goto("admin_menu")
    
    
    #* Back to SelectRoomScene
    @on.message(F.text == ButtonLabel.BACK.value)
    async def back(self, message: Message, session: AsyncSession):
        await message.delete()
        # RoomSelectScene.on_enter() requires database session
        await self.wizard.back(session=session)
    
    
    #* GOTO other scenes handlers
    @on.message(F.text == RoomManagementMenu.EDIT_ROOM.value)
    async def to_room_edit(self, message: Message):
        await message.delete()
        await self.wizard.update_data(flag_room_act=RoomManagementMenu.EDIT_ROOM.value) 
        await self.wizard.goto("room_edit_scene")