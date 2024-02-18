import asyncio
import logging
import sys
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config_data.config import load_config
from keyboards.set_menu import set_main_menu

from middlewares.db import DataBaseSession
from database.engine import create_db, session_maker

from utils.logger import Logger

from handlers.custom_kb_handler import kb_router
from handlers.admin.user_management import user_management_router
from handlers.admin.room_management import room_management_router
from handlers.admin.desk_management import desk_management_router

logger = Logger()

config = load_config()
bot = Bot(token=config.bot.token, parse_mode=ParseMode.HTML)

dp = Dispatcher()
dp.include_router(kb_router)
dp.include_router(user_management_router)
dp.include_router(room_management_router)
dp.include_router(desk_management_router)

async def on_startup(bot):
    await create_db()

    bot_info = await bot.me()
    logger.info(
        f"Bot: {bot_info.username} started on {datetime.now().replace(microsecond=0)}"
    )

async def on_shutdown(bot):
    bot_info = await bot.me()
    logger.info(
        f"Bot: {bot_info.username} shut down on {datetime.now().replace(microsecond=0)}"
    )

async def main():
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    
    #! engine = create_sa_engine(url=config.db.url)
    #! session_factory = create_sa_session_factory(engine)

    await bot.delete_webhook(drop_pending_updates=True)
    await set_main_menu(bot)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        ...