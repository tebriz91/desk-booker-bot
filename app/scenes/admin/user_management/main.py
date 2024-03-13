from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, on

from misc.const.admin_menu import UserManagementMenu
from misc.const.button_labels import ButtonLabel
from keyboards.reply import create_reply_kb

class UserManagementScene(Scene, state="user_management"): # TODO: rename state to user_management_scene and update in other files
    
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        keyboard = create_reply_kb(
            buttons=[
                UserManagementMenu.ADD_USER.value,
                UserManagementMenu.DELETE_USER.value,
                UserManagementMenu.EDIT_USER.value,
                UserManagementMenu.BAN_USER.value,
                UserManagementMenu.UNBAN_USER.value,
                UserManagementMenu.BROWSE_USERS.value],
            width=3,
            util_buttons=[
                ButtonLabel.BACK.value,
                ButtonLabel.EXIT.value],
            width_util=2,
            one_time_keyboard=True)
        
        await message.answer(
            text="User Management Menu",
            reply_markup=keyboard)
    
    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext) -> None:
        await message.delete()
        await message.answer(
            text="You've exited User Management Menu",
            reply_markup=ReplyKeyboardRemove())
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.exit()
    
    @on.message(F.text == ButtonLabel.BACK.value)
    async def back(self, message: Message):
        await message.delete()
        await self.wizard.back()

    #* GOTO other scenes handlers
    @on.message(F.text == UserManagementMenu.ADD_USER.value)
    async def to_user_add(self, message: Message):
        await message.delete()
        await self.wizard.goto("user_add")

    @on.message(F.text == UserManagementMenu.DELETE_USER.value)
    async def to_user_delete(self, message: Message):
        await message.delete()
        await self.wizard.goto("user_delete")