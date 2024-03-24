from typing import Any, List

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession

from misc.const.button_labels import ButtonLabel
from keyboards.inline import get_inline_keyboard

from services.common.rooms_list_generator import generate_available_rooms_list


class UserRoomSelectScene(Scene, state="user_room_select_scene"):
    
    @on.callback_query.enter()
    async def on_enter(self, query: CallbackQuery, session: AsyncSession) -> Any:
        
        rooms = await generate_available_rooms_list(session)
        
        keyboard = get_inline_keyboard(
            buttons=rooms,
            width=1 if len(rooms) <= 7 else 2,
            util_buttons=[
                ButtonLabel.EXIT.value,
                ButtonLabel.BACK.value],
            width_util=2)
        
        await query.message.edit_text(
            text="Select room",
            reply_markup=keyboard)

    @on.callback_query.exit()
    async def on_exit(self, query: CallbackQuery) -> None:
        await self.wizard.clear_data()
        await query.message.edit_text(text='Process finished')
    
    @on.callback_query(F.data == ButtonLabel.EXIT.value)
    async def exit(self, query: CallbackQuery) -> None:
        await self.wizard.exit()

    @on.callback_query(F.data == ButtonLabel.BACK.value)
    async def back(self, query: CallbackQuery) -> None:
        await query.message.delete()
        await self.wizard.back()