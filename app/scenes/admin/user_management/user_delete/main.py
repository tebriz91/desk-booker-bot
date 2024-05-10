from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from app.misc.const.admin_menu import UserDeleteMenu
from app.misc.const.button_labels import ButtonLabel
from app.keyboards.reply import get_reply_keyboard


class UserDeleteScene(Scene, state="user_delete_scene"):
    
    
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        keyboard = get_reply_keyboard(
            buttons=[
                UserDeleteMenu.SELECT_USER.value,
                UserDeleteMenu.DELETE_BY_ID.value,
                UserDeleteMenu.DELETE_BY_USERNAME.value],
            width=3,
            util_buttons=[
                ButtonLabel.TO_MAIN_MENU.value,
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=3,
            one_time_keyboard=False) # TODO: Set to True after implementing all handlers

        await message.answer(
            text="User Delete Menu",
            reply_markup=keyboard)
    
    
    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited User Delete Menu",
            reply_markup=ReplyKeyboardRemove())
    
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.clear_data()
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
    
    
    #* GOTO other scenes handlers
    @on.message(F.text == UserDeleteMenu.SELECT_USER.value)
    async def to_user_select_to_delete(self, message: Message): # TODO: Implement
        await message.delete()
        await message.answer("Not implemented yet.")
        # await self.wizard.goto("user_select_to_delete")


    @on.message(F.text == UserDeleteMenu.DELETE_BY_ID.value)
    async def to_user_delete_by_id(self, message: Message):
        await message.delete()
        await self.wizard.goto("user_delete_by_id_scene")


    @on.message(F.text == UserDeleteMenu.DELETE_BY_USERNAME.value)
    async def to_user_delete_by_username(self, message: Message):
        await message.delete()
        await self.wizard.goto("user_delete_by_username_scene")