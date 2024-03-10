from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, on

from misc.const.admin_menu import UserDeleteMenu
from misc.const.button_labels import ButtonLabel
from keyboards.reply import create_reply_kb

class UserDeleteScene(Scene, state="user_delete"):
    
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        keyboard = create_reply_kb(
            buttons=[
                UserDeleteMenu.SELECT_USER.value,
                UserDeleteMenu.DELETE_BY_ID.value,
                UserDeleteMenu.DELETE_BY_USERNAME.value],
            width=3,
            util_buttons=[
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=2,
            one_time_keyboard=True)

        await message.answer(
            text="User Delete Menu",
            reply_markup=keyboard)
    
    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext) -> None:
        await message.delete()
        await message.answer(
            text="You've exited User Delete Menu",
            reply_markup=ReplyKeyboardRemove())
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.exit()
    
    @on.message(F.text == ButtonLabel.BACK.value)
    async def back(self, message: Message):
        await message.delete()
        await self.wizard.back()

    #* GOTO other scenes handlers
    @on.message(F.text == UserDeleteMenu.SELECT_USER.value)
    async def to_user_select_to_delete(self, message: Message):
        await message.delete()
        await self.wizard.goto("user_select_to_delete")

    @on.message(F.text == UserDeleteMenu.DELETE_BY_ID.value)
    async def to_user_delete_by_id(self, message: Message):
        await message.delete()
        await self.wizard.goto("user_delete_by_id")

    @on.message(F.text == UserDeleteMenu.DELETE_BY_USERNAME.value)
    async def to_user_delete_by_username(self, message: Message):
        await message.delete()
        await self.wizard.goto("user_delete_by_username")