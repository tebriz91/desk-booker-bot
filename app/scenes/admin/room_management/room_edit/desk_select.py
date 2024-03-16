from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession

from misc.const.admin_menu import RoomEditMenu
from misc.const.button_labels import ButtonLabel

from database.orm_queries import orm_select_desks_by_room_name
from keyboards.reply import create_reply_kb

class DeskSelectScene(Scene, state="desk_select_scene"):

    @on.message.enter()
    async def on_enter(self, message: Message, session: AsyncSession) -> Any:
        """
        Do not forget to pass session to the on_enter()
        """
        data = await self.wizard.get_data()
        room_name = data.get('room_name')
        desks_orm_obj = await orm_select_desks_by_room_name(session, room_name) # TODO: Move this logic to a service
        desks = [desks.name for desks in desks_orm_obj]
        keyboard = create_reply_kb(
            buttons=desks,
            width=3 if len(desks) > 5 else 2,
            util_buttons=[
                ButtonLabel.TO_MAIN_MENU.value,
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=3,
            one_time_keyboard=True)

        await message.answer(
            text=f'Choose desk in room: {room_name}',
            reply_markup=keyboard)

    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Desk Select Menu",
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
    async def process_desk_name_button(self, message: Message):
        await message.delete()
        await self.wizard.update_data(desk_name=message.text)
        data = await self.wizard.get_data()
        flag_desk_act = data.get("flag_desk_act")
        if flag_desk_act == RoomEditMenu.EDIT_DESK.value:
            await self.wizard.goto("desk_edit_scene")
        elif flag_desk_act == RoomEditMenu.DELETE_DESK.value:
            await self.wizard.goto("desk_delete_scene")
        else:
            raise Exception("flag_desk_act is not set in RoomEditScene")