from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, on

from misc.const.admin_menu import AdminMenu
from misc.const.button_labels import ButtonLabel
from keyboards.reply import create_reply_kb

class AdminMenuScene(Scene, state="admin_menu"):
    """
    This class represents the Admin Menu scene. It is the first scene.
    It is triggered by the /admin command. Entry-point handler is defined in the setup.py file and is registered to the admin_router.
    """
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        """
        This method is called when the admin enters the admin menu scene.
        
        :param message: The message object.
        :return:
        """ 
        keyboard = create_reply_kb(
            buttons=[
                AdminMenu.USER_MANAGEMENT.value,
                AdminMenu.ROOM_MANAGEMENT.value,
                AdminMenu.BOOKING_MANAGEMENT.value,
                AdminMenu.ANALYTICS.value],
            width=2,
            util_buttons=[
                ButtonLabel.EXIT.value],
            width_util=1,
            one_time_keyboard=True)
        
        await message.answer(
            text="Admin Menu",
            reply_markup=keyboard)

    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext) -> None:
        """
        This method is called when the admin exits the admin panel scene.
        
        It displays a message to the admin and removes the keyboard.
        
        :param message: The message object.
        :return:
        """
        # Answer the user and remove keyboard       
        await message.delete()
        await message.answer(
            text="You've exited Admin Menu",
            reply_markup=ReplyKeyboardRemove())
        
    @on.message(F.text == ButtonLabel.EXIT.value)
    async def exit(self, message: Message):
        """
        This handler is called when the admin clicks the "Exit" button.
        """
        await self.wizard.exit()

    #* GOTO other scenes handlers
    @on.message(F.text == AdminMenu.USER_MANAGEMENT.value)
    async def to_user_management(self, message: Message):
        await message.delete()
        await self.wizard.goto("user_management")

    @on.message(F.text == AdminMenu.ROOM_MANAGEMENT.value)
    async def to_room_management(self, message: Message):
        await message.delete()
        await self.wizard.goto("room_management_scene")

    @on.message(F.text == AdminMenu.BOOKING_MANAGEMENT.value)
    async def to_booking_management(self, message: Message):
        await message.delete()
        await self.wizard.goto("booking_management")

    @on.message(F.text == AdminMenu.ANALYTICS.value)
    async def to_analytics(self, message: Message):
        await message.delete()
        await self.wizard.goto("analytics")
