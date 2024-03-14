from aiogram import F, Router
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession

from routers.admin.router import admin_router

from database.orm_queries import orm_insert_desk_with_room_id, orm_select_desks_by_room_id

from utils.logger import Logger

logger = Logger()

@admin_router.message(F.text.startswith("/get_desks"))
async def command_get_desks_by_room_id_handler(message: Message, session: AsyncSession):
    command_name, room_id = message.text.split(sep=" ")
    room_id = int(room_id)
    desks = await orm_select_desks_by_room_id(session, room_id=room_id)
    for desk in desks:
        await message.answer(f"id: {desk.id}, name: {desk.name}, availability: {desk.availability}, additional_info: {desk.additional_info}")

@admin_router.message(F.text.startswith("/add_desk"))
async def command_add_desk_handler(message: Message, session: AsyncSession):
    command_name, room_id, desk_name = message.text.split(sep=" ")
    logger.info(f"room_id: {room_id}, desk_name: {desk_name}")
    room_id = int(room_id)
    try:
        await orm_insert_desk_with_room_id(session, room_id, desk_name)
        await message.answer(f"Desk with name: {desk_name} in room with id: {room_id} added to database")
    except Exception as e:
        logger.error(e)
        await message.answer(f"Desk with name: {desk_name} already exists in database")