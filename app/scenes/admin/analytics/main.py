from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, on


class AnalyticsScene(Scene, state="analytics_scene"):
    
    #* The scene's entry point is designed to handle callback queries.
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        # Create reply keyboard
        keyboard = ReplyKeyboardBuilder()
        keyboard.button(text="Analytics for a User")
        keyboard.button(text="Analytics for a Room")
        keyboard.button(text="Analytics for a Desk")
        keyboard.button(text="Analytics for All Users")
        keyboard.button(text="Analytics for All Rooms")
        keyboard.button(text="Analytics for All Desks")
        keyboard.button(text="Analytics for All Bookings")
        keyboard.button(text="Back")
        keyboard.button(text="Exit")

        await message.answer(
            text="Analytics Menu",
            reply_markup=keyboard.adjust(2).as_markup(resize_keyboard=True))
    
    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Analytics Menu",
            reply_markup=ReplyKeyboardRemove())
    
    @on.message(F.text == "Exit")
    async def exit(self, message: Message):
        await self.wizard.exit()

    @on.message(F.text == "Back")
    async def back(self, message: Message):
        await message.delete()
        await self.wizard.back()