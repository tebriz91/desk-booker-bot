from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_insert_room, orm_select_rooms

from utils.logger import Logger

logger = Logger()

room_management_router = Router()

@room_management_router.message(Command("rooms"))
async def command_get_rooms_handler(message: Message, session: AsyncSession):
    rooms = await orm_select_rooms(session)
    for room in rooms:
        await message.answer(f"id: {room.id}, name: {room.name}, availability: {room.availability}, plan: {room.plan}, additional_info: {room.additional_info}")

@room_management_router.message(F.text.startswith("/add_room"))
async def command_add_room_handler(message: Message, session: AsyncSession):
    command_name, room_name = message.text.split(sep=" ")
    logger.info(f"room_name: {room_name}")
    try:
        await orm_insert_room(session, {"name": room_name})
        await message.answer(f"Room with name: {room_name} added to database")
    except Exception as e:
        logger.error(e)
        await message.answer(f"Room with name: {room_name} already exists in database")