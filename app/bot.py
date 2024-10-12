import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.fsm.storage.redis import (
    DefaultKeyBuilder,
    RedisStorage,
)
from aiogram_dialog import setup_dialogs
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config_data.config import Config, load_config  # noqa: E402
from app.database.engine import get_engine, get_session_pool  # noqa: E402
from app.dialogs import register_dialogs  # noqa: E402
from app.keyboards.set_menu import set_main_menu  # noqa: E402

# from app.middlewares.config_middleware import ConfigMiddleware
from app.middlewares.db_middleware import DataBaseSession  # noqa: E402
from app.middlewares.i18n import TranslatorRunnerMiddleware  # noqa: E402
from app.middlewares.user_middleware import UserMiddleware  # noqa: E402
from app.routers import router  # noqa: E402
from app.scenes.setup import register_scenes  # noqa: E402
from app.utils.bot_description import set_bot_description  # noqa: E402
from app.utils.i18n import Translator  # noqa: E402
from app.utils.logger import Logger  # noqa: E402

logger = Logger()


config: Config = load_config()


def setup_bot() -> Tuple[Bot, RedisStorage]:
    """
    Initializes the bot with token and properties defined in the config.
    Sets up Redis storage for managing state and sessions.
    """
    redis = Redis(host=config.redis.host, port=config.redis.port)
    key_builder = DefaultKeyBuilder(with_destiny=True)
    storage = RedisStorage(redis=redis, key_builder=key_builder)

    # Create an instance of DefaultBotProperties
    default_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)

    # Initialize the bot with the default properties
    bot = Bot(
        token=config.bot.token,
        session=AiohttpSession(),
        default=default_properties,
    )

    return bot, storage


def setup_dispatcher(bot, storage) -> Dispatcher:
    """
    Configures the Dispatcher with the bot instance and storage.
    Includes routers and registers scenes.
    """
    dp = Dispatcher(
        storage=storage,
        events_isolation=SimpleEventIsolation(),
    )
    dp.include_router(router)
    register_dialogs(router)  # Initialize all dialog modules
    setup_dialogs(dp)  # Initialize DialogManager and register dialogs
    register_scenes(dp)  # Initialize SceneRegistry and register scenes
    dp.workflow_data.update(
        config=config
    )  # Make config available globally through dispatcher
    return dp


def setup_database() -> async_sessionmaker[AsyncSession]:
    engine = get_engine(db_url=config.db.url, echo=False)
    session_pool = get_session_pool(engine)
    return session_pool


def setup_middlewares(dp, session_pool) -> None:
    """Applies middlewares to the Dispatcher for
    pre-processing messages and updates."""
    dp.message.outer_middleware(UserMiddleware(session_pool=session_pool))
    dp.callback_query.outer_middleware(UserMiddleware(session_pool=session_pool))  # noqa
    dp.update.middleware(DataBaseSession(session_pool=session_pool))
    dp.update.middleware(TranslatorRunnerMiddleware(translator=Translator()))
    # dp.update.middleware(
    # ConfigMiddleware(config=config))


async def on_startup(bot):
    bot_info = await bot.me()
    logger.info(
        f"Bot: {bot_info.username} started on "
        f"{datetime.now().replace(microsecond=0)}"
    )


async def on_shutdown(bot):
    bot_info = await bot.me()
    logger.info(
        f"Bot: {bot_info.username} shut down on "
        f"{datetime.now().replace(microsecond=0)}"
    )


async def main():
    """
    The main coroutine setups bot, dispatcher, database, middlewares
    and starts polling for updates.
    """
    bot, storage = setup_bot()
    dp = setup_dispatcher(bot, storage)
    session_pool = setup_database()
    setup_middlewares(dp, session_pool)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await bot.delete_webhook(
        drop_pending_updates=True
    )  # Removes any existing webhooks before starting polling for updates
    await set_bot_description(bot)
    await set_main_menu(bot)  # Setup the bot's main menu
    await dp.start_polling(
        bot,
        _translator_hub=Translator(),
        allowed_updates=dp.resolve_used_update_types(),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Gracefully handle manual bot interruption via Ctrl+C
        pass
