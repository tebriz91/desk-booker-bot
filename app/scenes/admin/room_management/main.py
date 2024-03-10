from typing import Any

from aiogram import F
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, on

class RoomManagementScene(Scene, state="room_management"):
    
    #* The scene's entry point is designed to handle callback queries.
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        # Create reply keyboard
        keyboard = ReplyKeyboardBuilder()
        keyboard.button(text="Add Room")
        keyboard.button(text="Delete Room")
        keyboard.button(text="Edit Room")
        keyboard.button(text="Add Desk")
        keyboard.button(text="Delete Desk")
        keyboard.button(text="Edit Desk")
        keyboard.button(text="Show All Rooms")
        keyboard.button(text="Back")
        keyboard.button(text="Exit")

        await message.answer(
            text="Room Management Menu",
            reply_markup=keyboard.adjust(2).as_markup(resize_keyboard=True))
    
    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext) -> None:
        await message.delete()
        await message.answer(
            text="You've exited Room Management Menu",
            reply_markup=ReplyKeyboardRemove())
    
    @on.message(F.text == "Exit")
    async def exit(self, message: Message):
        await self.wizard.exit()

    @on.message(F.text == "Back")
    async def back(self, message: Message):
        await message.delete()
        await self.wizard.back()