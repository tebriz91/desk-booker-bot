from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession

from misc.const.admin_menu import RoomManagementMenu
from misc.const.button_labels import ButtonLabel

from database.orm_queries import orm_select_rooms
from keyboards.reply import create_reply_kb

class RoomSelectScene(Scene, state="room_select_scene"):

    @on.message.enter()
    async def on_enter(self, message: Message, session: AsyncSession) -> Any:
        """
        Do not forget to pass session to the on_enter()
        """
        rooms_orm_obj = await orm_select_rooms(session) # TODO: Move this logic to a service
        rooms = [rooms.name for rooms in rooms_orm_obj]
        keyboard = create_reply_kb(
            buttons=rooms,
            width=3 if len(rooms) > 5 else 2,
            util_buttons=[
                ButtonLabel.TO_MAIN_MENU.value,
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=3,
            one_time_keyboard=True)

        await message.answer(
            text='Choose room',
            reply_markup=keyboard)

    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Room Select Menu",
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
    
    #* GOTO other scenes handler
    @on.message(F.text)
    async def process_room_name_button(self, message: Message, session: AsyncSession):
        await message.delete()
        await self.wizard.update_data(room_name=message.text)
        data = await self.wizard.get_data()
        flag_room_act = data.get("flag_room_act")
        if flag_room_act == RoomManagementMenu.EDIT_ROOM.value:
            await self.wizard.goto("room_edit_scene")
        elif flag_room_act == RoomManagementMenu.DELETE_ROOM.value:
            await self.wizard.goto("room_delete_scene")
        elif flag_room_act == RoomManagementMenu.BROWSE_ROOMS.value:
            await self.wizard.goto("room_browse_scene", session=session) #RoomBrowseScene.on_enter() requires database session
        else:
            raise Exception("flag_room_act is not set in RoomSelectScene")