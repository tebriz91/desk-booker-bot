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
from database.engine import (
    initialize_engine,
    get_session_maker,
    create_db,
    drop_db #! For development purposes only
    )
from utils.logger import Logger
from routers import router


# Configuration Loading
config = load_config()


# Logger Setup
logger = Logger()


# Initialize the engine with DB URL from config
initialize_engine(config.db.url, echo=True)


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
def setup_middlewares(dp):
    """
    Applies middlewares to the Dispatcher for pre-processing messages and updates. This includes setting up session management and user data handling.
    """
    session_maker = get_session_maker()
    dp.message.outer_middleware(UserMiddleware(session_pool=session_maker)) # This middleware checks if the user is registered in the database
    dp.callback_query.outer_middleware(UserMiddleware(session_pool=session_maker))
    dp.update.middleware(DataBaseSession(session_pool=session_maker)) # This middleware provides a database session to the handler
    # dp.update.middleware(ConfigMiddleware(config=config))


async def on_startup(bot):
    bot_info = await bot.me()
    logger.info(
        f"Bot: {bot_info.username} started on {datetime.now().replace(microsecond=0)}")


async def on_shutdown(bot):
    bot_info = await bot.me()
    logger.info(
        f"Bot: {bot_info.username} shut down on {datetime.now().replace(microsecond=0)}")


async def main():
    """
    The main coroutine setups the bot, the dispatcher, and the middlewares.
    It handles startup events like database initialization, bot registration,
    middleware setup, and starts polling for updates.
    
    The flow is as follows:
    1. Initialize the database engine with the configuration from the config file.
    2. Create the database schema if it doesn't exist.
    3. Initialize the bot with its token and default properties.
    4. Setup the dispatcher with the bot instance and session storage.
    5. Apply middlewares for user session management and database access.
    6. Register the startup and shutdown events for logging and resource management.
    7. Delete any existing webhook configurations to ensure clean startup.
    8. Setup the bot's main menu for user interaction.
    9. Start polling for updates to begin processing incoming messages and commands.
    """
    # Initialize the database engine with configuration parameters.
    initialize_engine(config.db.url, echo=True)
    
    #! Drop the database schema if it exists. This is for development purposes only.
    # await drop_db()
    
    # Create the database schema based on defined models.
    # It doesn't affect existing tables that match the schema.
    await create_db()
    
    bot, storage = initialize_bot()
    dp = setup_dispatcher(bot, storage)
    setup_middlewares(dp)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await bot.delete_webhook(drop_pending_updates=True) # Remove any existing webhooks before starting to poll for updates
    await set_main_menu(bot) # Setup the bot's main menu
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Gracefully handle manual bot interruption via Ctrl+C
        pass