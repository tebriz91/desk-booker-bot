import asyncio
import logging
import sys
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.memory import SimpleEventIsolation

from config_data.config import load_config
from keyboards.set_menu import set_main_menu

from scenes.setup import register_scenes

from middlewares.user_middleware import UserMiddleware
# from middlewares.config_middleware import ConfigMiddleware
from middlewares.db_middleware import DataBaseSession
from database.engine import create_db, drop_db, session_maker

from utils.logger import Logger

from routers import router

logger = Logger()

config = load_config()
storage = MemoryStorage()
bot = Bot(
    token=config.bot.token,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
        link_preview_is_disabled=False,
        link_preview_prefer_large_media=True,
        link_preview_show_above_text=False))
dp = Dispatcher(
    events_isolation=SimpleEventIsolation(),
)
dp.include_router(router)

# Initialize SceneRegistry and register scenes
register_scenes(dp)

# Workflow data available in all handlers and middlewares
dp.workflow_data.update(config=config)

async def on_startup(bot):
    # await drop_db()
    await create_db()
    bot_info = await bot.me()
    logger.info(
        f"Bot: {bot_info.username} started on {datetime.now().replace(microsecond=0)}")

async def on_shutdown(bot):
    bot_info = await bot.me()
    logger.info(
        f"Bot: {bot_info.username} shut down on {datetime.now().replace(microsecond=0)}")

async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.message.outer_middleware(UserMiddleware(session_pool=session_maker))
    dp.callback_query.outer_middleware(UserMiddleware(session_pool=session_maker))
    # dp.update.middleware(ConfigMiddleware(config=config))
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    
    await bot.delete_webhook(drop_pending_updates=True)
    await set_main_menu(bot)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        ...