from aiogram.filters import Command
from aiogram.types import Message

from routers.admin.router import admin_router

from keyboards.admin_kb import create_admin_kb

from enums.admin_kb_buttons import AdminKB

@admin_router.message(Command("admin"))
async def command_admin_handler(message: Message):
    await message.answer(
        text="Admin menu",
        reply_markup=create_admin_kb(
            buttons = [
                AdminKB.USER_MANAGEMENT.value,
                AdminKB.ROOM_MANAGEMENT.value,
                AdminKB.BOOKING_MANAGEMENT.value,
                AdminKB.ANALYTICS.value
            ],
            sizes=2))