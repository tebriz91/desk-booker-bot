<<<<<<< HEAD
from typing import Any
=======
from typing import Any, Union
>>>>>>> 9ead955e717c190c7a83d0e1aa1f4102a4929b44

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

<<<<<<< HEAD
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, on

from misc.const.admin_menu import AdminMenu
from misc.const.button_labels import ButtonLabel
from keyboards.reply import create_reply_kb

class AdminMenuScene(Scene, state="admin_menu"):
    """
    This class represents the Admin Menu scene. It is the first scene.
    It is triggered by the /admin command. Entry-point handler is defined in the setup.py file and is registered to the admin_router.
=======
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, on

from keyboards.admin_kb import create_admin_kb

from enums.admin_kb_buttons import AdminKB


class AdminPanelScene(Scene, state="admin_panel"):
    """
    This class represents the admin panel scene.
    It inherits from the Scene class and has a state of "admin_panel".
    It is registered in the admin_router.
>>>>>>> 9ead955e717c190c7a83d0e1aa1f4102a4929b44
    """
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        """
<<<<<<< HEAD
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
=======
        This method is called when the admin enters the admin panel scene.
        
        It displays the admin panel reply keyboard.
        
        :param message: The message object.
        :param step: Scene argument, can be passed to the scene using the wizard
        :return:
        """ 
        # Create reply keyboard
        keyboard = ReplyKeyboardBuilder()
        keyboard.button(text=AdminKB.USER_MANAGEMENT.value)
        keyboard.button(text=AdminKB.ROOM_MANAGEMENT.value)
        keyboard.button(text=AdminKB.BOOKING_MANAGEMENT.value)
        keyboard.button(text=AdminKB.ANALYTICS.value)     
        keyboard.button(text="Exit")
        
        await message.answer(
            text="Admin Panel",
            reply_markup=keyboard.adjust(2).as_markup(resize_keyboard=True))

    @on.message(F.text == AdminKB.USER_MANAGEMENT.value)
    async def to_user_management(self, message: Message):
        # Transition to the User Management scene
        await message.delete()
        await self.wizard.goto("user_management")

    @on.message(F.text == AdminKB.ROOM_MANAGEMENT.value)
    async def to_room_management(self, message: Message):
        # Transition to the Room Management scene
        await message.delete()
        await self.wizard.goto("room_management")

    @on.message(F.text == AdminKB.BOOKING_MANAGEMENT.value)
    async def to_booking_management(self, message: Message):
        # Transition to the Booking Management scene
        await message.delete()
        await self.wizard.goto("booking_management")

    @on.message(F.text == AdminKB.ANALYTICS.value)
    async def to_analytics(self, message: Message):
        # Transition to the Analytics scene
        await message.delete()
        await self.wizard.goto("analytics")
>>>>>>> 9ead955e717c190c7a83d0e1aa1f4102a4929b44

    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext) -> None:
        """
        This method is called when the admin exits the admin panel scene.
        
<<<<<<< HEAD
        It displays a message to the admin and removes the keyboard.
=======
        It displays a message to the admin.
>>>>>>> 9ead955e717c190c7a83d0e1aa1f4102a4929b44
        
        :param message: The message object.
        :return:
        """
        # Answer the user and remove keyboard       
        await message.delete()
        await message.answer(
<<<<<<< HEAD
            text="You've exited Admin Menu",
            reply_markup=ReplyKeyboardRemove())
        
    @on.message(F.text == ButtonLabel.EXIT.value)
=======
            text="You've exited Admin Panel Menu",
            reply_markup=ReplyKeyboardRemove())
        

    @on.message(F.text == "Exit")
>>>>>>> 9ead955e717c190c7a83d0e1aa1f4102a4929b44
    async def exit(self, message: Message):
        """
        This handler is called when the admin clicks the "Exit" button.
        """
<<<<<<< HEAD
        await self.wizard.exit()

    #* GOTO other scenes handlers
    @on.message(F.text == AdminMenu.USER_MANAGEMENT.value)
    async def to_user_management(self, message: Message):
        await message.delete()
        await self.wizard.goto("user_management")

    @on.message(F.text == AdminMenu.ROOM_MANAGEMENT.value)
    async def to_room_management(self, message: Message):
        await message.delete()
        await self.wizard.goto("room_management")

    @on.message(F.text == AdminMenu.BOOKING_MANAGEMENT.value)
    async def to_booking_management(self, message: Message):
        await message.delete()
        await self.wizard.goto("booking_management")

    @on.message(F.text == AdminMenu.ANALYTICS.value)
    async def to_analytics(self, message: Message):
        await message.delete()
        await self.wizard.goto("analytics")
=======
        await self.wizard.exit()
>>>>>>> 9ead955e717c190c7a83d0e1aa1f4102a4929b44
