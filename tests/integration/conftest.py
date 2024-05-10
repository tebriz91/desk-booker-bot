import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import pytest
import pytest_asyncio

from tests.integration.mocked_bot import MockedBot
from aiogram_dialog.test_tools import MockMessageManager, BotClient

from aiogram import Dispatcher
from aiogram_dialog import setup_dialogs
from aiogram.fsm.storage.memory import (
    MemoryStorage,
    # DisabledEventIsolation,
    # SimpleEventIsolation,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
# from redis.asyncio.connection import parse_url as parse_redis_url
# from aiogram.fsm.storage.redis import RedisEventIsolation, RedisStorage

from app.config_data.config import Config, load_config
from app.utils.i18n import Translator

from app.dialogs import register_dialogs
from app.middlewares.i18n import TranslatorRunnerMiddleware
from app.middlewares.db_middleware import DataBaseSession
from app.middlewares.user_middleware import UserMiddleware
from app.routers import router


from app.utils.logger import Logger
logger = Logger()


@pytest.fixture(scope="session")
def config():
    logger.info("Loading config.")
    config = load_config()
    if not config:
        logger.error("Failed to load configuration.")
    else:
        logger.info("Configuration loaded successfully:")
        logger.info(f"Database URL: {config.db.url}")
        logger.info(f"Redis Host: {config.redis.host}")
        logger.info(f"Redis Port: {config.redis.port}")
        logger.info(f"Bot Token: {config.bot.token}")
        logger.info(f"Operation Days: {config.bot_operation.num_days}, Exclude Weekends: {config.bot_operation.exclude_weekends}")
        logger.info(f"Advanced Mode: {config.bot_operation.advanced_mode}")
        logger.info(f"Timezone: {config.bot_operation.timezone}, Country code: {config.bot_operation.country_code}")
        logger.info(f"Date format: {config.bot_operation.date_format}")
    
    return config


@pytest.fixture(scope="session")
def bot(config: Config) -> MockedBot:
    logger.info("Creating bot with token: %s", config.bot.token)
    return MockedBot(token=config.bot.token)


@pytest.fixture()
def i18n():
    translator_hub = Translator()
    return translator_hub.translator_hub.get_translator_by_locale(locale="en")


@pytest.fixture(scope="session")
def engine(config: Config):
    logger.info("Creating engine.")
    engine = create_async_engine(config.db.url, echo=False)
    yield engine
    # engine.sync_engine.dispose()


@pytest.fixture(scope="session")
def dp(engine,
       message_manager: MockMessageManager,
       bot: MockedBot,
       config: Config,
       ) -> Dispatcher:
    logger.info("Creating session pool.")
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    
    logger.info("Creating dispatcher.")
    dispatcher = Dispatcher(storage=MemoryStorage(),
                            bot=bot)
    
    logger.info("Creating translator and setting global language.")
    tranlator = Translator(global_lang="en")
    
    dispatcher['config'] = config
    # dispatcher['i18n'] = mock_translator
    
    dispatcher.include_router(router)
    register_dialogs(router)
    setup_dialogs(dispatcher, message_manager=message_manager)
    dispatcher.update.middleware(TranslatorRunnerMiddleware(translator=tranlator))
    dispatcher.message.outer_middleware(UserMiddleware(session_pool=sessionmaker))
    dispatcher.callback_query.outer_middleware(UserMiddleware(session_pool=sessionmaker))
    dispatcher.update.middleware(DataBaseSession(session_pool=sessionmaker))

    return dispatcher


@pytest_asyncio.fixture(scope="function")
async def session(engine):
    logger.info("Creating database session.")
    async with AsyncSession(engine) as s:
        yield s


@pytest.fixture(scope="session")
def message_manager():
    logger.info("Creating message manager.")
    return MockMessageManager()


# Commented it out because manually set it up in the test functions
# @pytest.fixture(autouse=True) # autouse=True means that this fixture will be automatically used by all test functions
# def reset_message_manager(message_manager: MockMessageManager):
#     yield
#     message_manager.reset_history()


@pytest.fixture
def user_client(dp: Dispatcher, bot: MockedBot):
    logger.info("Creating user client for testing.")
    return BotClient(dp, bot=bot)


@pytest.fixture(scope="session")
def event_loop():
    """Fixture providing an asyncio event loop for test sessions.

    This fixture creates and yields an asyncio event loop suitable for running
    asynchronous tests. It also ensures that the event loop policy is set correctly for
    Windows systems using Python 3.8 or higher.

    :return: asyncio.AbstractEventLoop: An asyncio event loop for running asynchronous
    tests.
    """
    if sys.platform.startswith("win") and sys.version_info[:2] >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()
    asyncio.set_event_loop(None)