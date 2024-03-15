import asyncio
import logging
import sys
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, Redis, DefaultKeyBuilder
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

# Configuration Loading
config = load_config()

# Logger Setup
logger = Logger()

# Bot Initialization
def initialize_bot():
    """
    Initializes the bot with token and properties defined in the config.
    Sets up Redis storage for managing state and sessions.
    """
    redis = Redis(host=config.redis.host, port=config.redis.port)
    key_builder = DefaultKeyBuilder(with_destiny=True)
    storage = RedisStorage(redis=redis, key_builder=key_builder)
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML, # HTML as default parse mode for messages
            link_preview_is_disabled=False, # Enable link previews
            link_preview_prefer_large_media=True,
            link_preview_show_above_text=False)) # Show link previews below text
    return bot, storage

# Dispatcher Setup
def setup_dispatcher(bot, storage):
    """
    Configures the Dispatcher with the bot instance and storage mechanism.
    Includes routers and registers scenes for handling different bot commands and interactions.
    """    
    dp = Dispatcher(
        storage=storage,
        events_isolation=SimpleEventIsolation(),
    )
    dp.include_router(router)
    register_scenes(dp) # Initialize SceneRegistry and register scenes
    dp.workflow_data.update(config=config) # Make config available globally through dispatcher
    return dp

# Middleware Setup
def setup_middlewares(dp, session_maker):
    """
    Applies middlewares to the Dispatcher for pre-processing messages and updates. This includes setting up session management and user data handling.
    """
    dp.message.outer_middleware(UserMiddleware(session_pool=session_maker)) # This middleware checks if the user is registered in the database
    dp.callback_query.outer_middleware(UserMiddleware(session_pool=session_maker))
    dp.update.middleware(DataBaseSession(session_pool=session_maker)) # This middleware provides a database session to the handler
    # dp.update.middleware(ConfigMiddleware(config=config))

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
    """
    Main coroutine that setups the bot, dispatcher, and middlewares.
    It registers startup and shutdown events, sets up the main menu, and starts polling for updates.
    """
    bot, storage = initialize_bot()
    dp = setup_dispatcher(bot, storage)
    setup_middlewares(dp, session_maker)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await bot.delete_webhook(drop_pending_updates=True) # Remove any existing webhooks before starting to poll for updates
    await set_main_menu(bot) # Setup the bot's main menu
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Gracefully handle manual bot interruption via Ctrl+C
        pass