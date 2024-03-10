from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, on

class BookingManagementScene(Scene, state="booking_management"):
    
    #* The scene's entry point is designed to handle callback queries.
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        # Create reply keyboard
        keyboard = ReplyKeyboardBuilder()
        keyboard.button(text="Show Past Bookings")
        keyboard.button(text="Show All Bookings for Room")
        keyboard.button(text="Show All Bookings for Desk")
        keyboard.button(text="Show All Bookings for User")
        keyboard.button(text="Cancel Booking")
        keyboard.button(text="Back")
        keyboard.button(text="Exit")

        await message.answer(
            text="Booking Management Menu",
            reply_markup=keyboard.adjust(2).as_markup(resize_keyboard=True))

    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Booking Management Menu",
            reply_markup=ReplyKeyboardRemove())
    
    @on.message(F.text == "Exit")
    async def exit(self, message: Message):
        await self.wizard.exit()
    
    @on.message(F.text == "Back")
    async def back(self, message: Message):
        await message.delete()
        await self.wizard.back()

    #* GOTO other scenes handlers
    @on.message(F.text == "Cancel Booking")
    async def to_cancel_booking_menu(self, message: Message):        
        await message.delete()
        await self.wizard.goto("cancel_booking_menu")
    
    #* Show past bookings logic
    @on.message(F.text == "Show Past Bookings")
    async def show_past_bookings(self, message: Message):        
        await message.delete()
        
        # Create reply keyboard
        keyboard = ReplyKeyboardBuilder()
        keyboard.button(text="Past week")
        keyboard.button(text="Past two weeks")
        keyboard.button(text="Past month")
        keyboard.button(text="Back")
        keyboard.button(text="Exit")

        await message.answer(
            text="Select a time period to show past bookings",
            reply_markup=keyboard.adjust(2).as_markup(resize_keyboard=True))
    
    