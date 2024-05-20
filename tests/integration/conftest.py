import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import pytest
import pytest_asyncio
from typing import Any, Dict, Optional

from aiogram_dialog.test_tools import MockMessageManager, BotClient
from tests.integration.mocked_bot import MockedBot
from tests.integration.config import Config, load_config
from tests.integration.const import BOT_CONFIGURATIONS

from aiogram import Dispatcher
from aiogram_dialog import setup_dialogs
from aiogram.fsm.storage.memory import (
    MemoryStorage,
    # DisabledEventIsolation,
    # SimpleEventIsolation,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
# from redis.asyncio.connection import parse_url as parse_redis_url
# from aiogram.fsm.storage.redis import RedisEventIsolation, RedisStorage

from app.utils.i18n import Translator

from app.dialogs import register_dialogs
from app.middlewares.i18n import TranslatorRunnerMiddleware
from app.middlewares.db_middleware import DataBaseSession
from app.middlewares.user_middleware import UserMiddleware
from app.routers import router

from app.utils.logger import Logger
logger = Logger(level=20)


@pytest.fixture(scope="session")
def config(request: pytest.FixtureRequest) -> Config:
    logger.debug("Loading configuration.")
    config_name: str = request.config.getoption("config", default="default")
    selected_config: Optional[Dict[str, Any]] = BOT_CONFIGURATIONS.get(config_name)
    
    if selected_config:
        return load_config(overrides=selected_config)
    
    logger.debug("Using default configuration. No overrides.")
    return load_config()


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add a command line option to the pytest parser."""
    parser.addoption(
        "--config", action="store", default="default",
        help="Defines the test bot configuration to use: default, 1, 2, or 3, etc."
    )


@pytest.fixture(scope="session")
def bot(config: Config) -> MockedBot:
    logger.debug("Creating bot with token: %s", config.bot.token)
    return MockedBot(token=config.bot.token)


@pytest.fixture()
def i18n() -> Translator:
    translator_hub = Translator()
    return translator_hub.translator_hub.get_translator_by_locale(locale="en")


@pytest.fixture(scope="session")
def engine(config: Config):
    logger.debug(f"Creating engine using DB URL: {config.db.url}.")
    engine = create_async_engine(config.db.url, echo=False)
    yield engine
    # engine.sync_engine.dispose()


@pytest.fixture(scope="session")
def dp(engine,
       message_manager: MockMessageManager,
       bot: MockedBot,
       config: Config,
       ) -> Dispatcher:
    logger.debug("Creating dispatcher.")
    
    dispatcher = Dispatcher(storage=MemoryStorage(),
                            bot=bot)
    
    dispatcher['config'] = config
    # dispatcher['i18n'] = mock_translator
    
    dispatcher.include_router(router)
    register_dialogs(router)
    setup_dialogs(dispatcher, message_manager=message_manager)
    
    tranlator = Translator(global_lang="en")
    dispatcher.update.middleware(TranslatorRunnerMiddleware(translator=tranlator))
        
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    
    dispatcher.message.outer_middleware(UserMiddleware(session_pool=sessionmaker))
    dispatcher.callback_query.outer_middleware(UserMiddleware(session_pool=sessionmaker))
    dispatcher.update.middleware(DataBaseSession(session_pool=sessionmaker))

    return dispatcher


@pytest_asyncio.fixture(scope="function")
async def session(engine):
    logger.debug("Creating database session.")
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as s:
        yield s
        await s.rollback()


@pytest.fixture(scope="session")
def message_manager():
    logger.debug("Creating message manager.")
    manager = MockMessageManager()
    yield manager
    logger.debug("Resetting message manager.")
    manager.reset_history()


# Commented it out because manually set it up in the test functions
# @pytest.fixture(autouse=True) # autouse=True means that this fixture will be automatically used by all test functions
# def reset_message_manager(message_manager: MockMessageManager):
#     yield
#     message_manager.reset_history()


@pytest.fixture(scope="session")
def user_client(dp: Dispatcher, bot: MockedBot) -> BotClient:
    logger.debug("Creating user client for testing.")
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