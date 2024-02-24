from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_select_users, orm_insert_user

from utils.logger import Logger

logger = Logger()

user_management_router = Router()

@user_management_router.message(Command("users"))
async def command_get_users_handler(message: Message, session: AsyncSession):
    users = await orm_select_users(session)
    for user in users:
        await message.answer(f"User_id: {user.id}, telegram_id: {user.telegram_id}, telegram_name: {user.telegram_name}")

@user_management_router.message(F.text.startswith("/add_user"))
async def command_add_user_handler(message: Message, session: AsyncSession):
    command_name, telegram_id, telegram_name = message.text.split(sep=" ")
    telegram_id = int(telegram_id)
    logger.info(f"telegram_id: {telegram_id}, telegram_name: {telegram_name}")
    try:
        await orm_insert_user(session, telegram_id, telegram_name)
        await message.answer(f"User with id: {telegram_id} and name {telegram_name} added to database")
    except Exception as e:
        logger.error(e)
        await message.answer(f"User with id: {telegram_id} or name {telegram_name} already exists in database")