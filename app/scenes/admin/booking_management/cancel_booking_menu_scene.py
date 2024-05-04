from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram.fsm.scene import Scene, on


class CancelBookingMenuScene(Scene, state="cancel_booking_menu_scene"):
    
    
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        # Create reply keyboard
        keyboard = ReplyKeyboardBuilder()
        keyboard.button(text="Select Room")
        keyboard.button(text="Back")
        keyboard.button(text="Exit")

        await message.answer(
            text="Cancel Booking Menu",
            reply_markup=keyboard.adjust(2).as_markup(resize_keyboard=True))
    
    
    @on.message(F.text == "Select Room")
    async def to_select_room_menu(self, message: Message):
        # Transition to the Booking Management scene
        await self.wizard.goto("select_room_menu")
    
    
    @on.message.exit()
    async def on_exit(self, message: Message) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Cancel Booking Menu",
            reply_markup=ReplyKeyboardRemove())
    
    
    @on.message(F.text == "Exit")
    async def exit(self, message: Message):
        await self.wizard.exit()
    
    
    @on.message(F.text == "Back")
    async def back(self, message: Message):
        await message.delete()
        await self.wizard.back()