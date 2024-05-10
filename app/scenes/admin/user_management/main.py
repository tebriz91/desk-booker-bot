from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.scene import Scene, on

from app.misc.const.admin_menu import UserManagementMenu
from app.misc.const.button_labels import ButtonLabel
from app.keyboards.reply import get_reply_keyboard


class UserManagementScene(Scene, state="user_management_scene"):
    
    
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        keyboard = get_reply_keyboard(
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
            one_time_keyboard=False) # TODO: Set to True after implementing all handlers
        
        await message.answer(
            text="User Management Menu",
            reply_markup=keyboard)
    
    
    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited User Management Menu",
            reply_markup=ReplyKeyboardRemove())
    
    
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        await self.wizard.clear_data()
        await self.wizard.exit()
    
    
    @on.message(F.text == ButtonLabel.BACK.value)
    async def back(self, message: Message):
        await message.delete()
        await self.wizard.clear_data()
        await self.wizard.back()


    #* GOTO other scenes handlers
    @on.message(F.text == UserManagementMenu.ADD_USER.value)
    async def to_user_add(self, message: Message):
        await message.delete()
        await self.wizard.goto("user_add_scene")


    @on.message(F.text == UserManagementMenu.DELETE_USER.value)
    async def to_user_delete(self, message: Message):
        await message.delete()
        await self.wizard.goto("user_delete_scene")
    
    
    @on.message(F.text == UserManagementMenu.EDIT_USER.value)
    async def to_user_edit(self, message: Message): # TODO: Implement
        await message.delete()
        await message.answer("Not implemented yet.")
        # await self.wizard.goto("user_edit_scene")
    
    
    @on.message(F.text == UserManagementMenu.BAN_USER.value)
    async def to_user_ban(self, message: Message): # TODO: Implement
        await message.delete()
        await message.answer("Not implemented yet.")
        # await self.wizard.goto("user_ban_scene")
    
    
    @on.message(F.text == UserManagementMenu.UNBAN_USER.value)
    async def to_user_unban(self, message: Message): # TODO: Implement
        await message.delete()
        await message.answer("Not implemented yet.")
        # await self.wizard.goto("user_unban_scene")
    
    
    @on.message(F.text == UserManagementMenu.BROWSE_USERS.value)
    async def to_user_browse(self, message: Message): # TODO: Implement
        await message.delete()
        await message.answer("Not implemented yet.")
        # await self.wizard.goto("user_browse_scene")