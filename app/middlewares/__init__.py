# TODO: Setup middlewares for the bot
'''
from aiogram import Dispatcher
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from middlewares.config_middleware import ConfigMiddleware
from middlewares.db_middleware import DataBaseSession
from config_data.config import BotConfig


def setup_middlewares(
    dp: Dispatcher,
    pool: async_sessionmaker[AsyncSession],
    bot_config: BotConfig):
    dp.message.middleware(ConfigMiddleware(bot_config))
    dp.message.middleware(DataBaseSession(pool))
'''