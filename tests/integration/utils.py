from math import exp
from typing import Callable, Any, List
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from aiogram.types import Message, CallbackQuery
from aiogram_dialog.test_tools import MockMessageManager, BotClient
from aiogram_dialog.test_tools.keyboard import InlineButtonTextLocator, InlineButtonPositionLocator

from app.database.models import Base
from app.utils.logger import Logger
logger = Logger(level=10)


async def insert_record(
    session: AsyncSession, 
    insert_function: Callable[[AsyncSession, Any], Any], 
    data: Any, 
    entity_name: str
) -> bool:
    """
    Generic insert function to handle adding entities to the database.
    This version does not commit or rollback, as these actions will be managed externally.
    
    Args:
        session (AsyncSession): The database session to use.
        insert_function (Callable): The function to use for inserting data.
        data (Any): The data to insert.
        entity_name (str): The name of the entity being inserted, for logging purposes.

    Returns:
        bool: True if insertion was successful, False otherwise.
    """
    try:
        await insert_function(session, data)
        logger.info(f"{entity_name.capitalize()} have been added to the database.")
        return True
    except Exception as e:
        logger.error(f"Failed to insert {entity_name}: {e}")
        return False


async def create_db(engine: AsyncEngine) -> None:
    """
    Create all database tables defined in the Base metadata.

    Args:
        engine (AsyncEngine): The database engine to use for creating tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def truncate_db_cascade(session: AsyncSession) -> None:
    """
    Truncate all tables in the database, cascading to all dependent tables.

    Args:
        session (AsyncSession): The database session to use for truncation.
    """
    if session.in_transaction():
        await session.rollback()  # Ensure no transactions are open

    async with session.begin():
        await session.execute(text("SET CONSTRAINTS ALL DEFERRED;"))  # Optional

        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f"TRUNCATE TABLE {table.name} CASCADE;"))
            

def assert_message_text(message: Message, expected_text: str) -> None:
    """
    Assert that the text of a message is equal to the expected value.

    Args:
        message (Message): The message to check.
        expected_text (str): The expected text value.
    """
    assert message.text == str(expected_text)
    logger.info(
        "Message text:\n\n"
        f"{message.text}\n\n"
        "Expected text:\n\n"
        f"{expected_text}\n"
    )


def log_sent_messages(message_manager: MockMessageManager) -> None:
    """
    Log the number of sent messages and their content.

    Args:
        message_manager (Any): The message manager containing sent messages.
    """
    logger.debug(f"Number of sent messages: {len(message_manager.sent_messages)}")
    for msg in message_manager.sent_messages:
        logger.debug(f"Message content: {msg.text}")
        

def log_inline_keyboard_buttons(message: Message) -> None:
    """
    Logs the text of all buttons in an inline keyboard.

    Args:
        message (Message): The message containing the inline keyboard.
    """
    if not message.reply_markup or not message.reply_markup.inline_keyboard:
        logger.debug("Message does not contain an inline keyboard.")
        return

    logger.debug("Listing all available buttons on UI:")
    for i, row in enumerate(message.reply_markup.inline_keyboard):
        for j, button in enumerate(row):
            logger.debug(f"Button at ({i},{j}): '{button.text}'")


def assert_inline_keyboard_buttons(expected_texts: List[str], message: Message) -> None:
    """
    Asserts that each expected text is found in the corresponding button in the inline keyboard.

    Args:
        expected_texts (List[str]): A list of expected texts to be found in the buttons.
        message (Message): The message containing the inline keyboard.
    """
    if not message.reply_markup or not message.reply_markup.inline_keyboard:
        logger.error("Message does not contain an inline keyboard.")
        assert False, "Message does not contain an inline keyboard."

    for expected_text in expected_texts:
        assert any(expected_text in button.text for row in message.reply_markup.inline_keyboard for button in row), f"Button with text '{expected_text}' not found in expected texts."
    logger.debug("All expected buttons found in the inline keyboard.")


async def click_inline_keyboard_button_by_location(
    user_client: BotClient,
    message: Message,
    row: int,
    column: int,
) -> str:
    """
    Click a button in the inline keyboard of a message and log the details.

    Args:
        user_client (BotClient): The bot client to simulate the button click.
        message (Message): The message containing the inline keyboard.
        row (int): The row index of the button.
        col (int): The column index of the button.

    Returns:
        str: The callback ID of the clicked button.

    Raises:
        AssertionError: If the button with the specified text is not found.
    """
    logger.debug(f"Clicking on the button at location ({row}, {column})")
    try:
        callback_id: str = await user_client.click(message, InlineButtonPositionLocator(row, column))
        logger.debug("Button click simulated successfully.")
        return callback_id
    except ValueError as e:
        logger.error(f"Failed to simulate button click: {e}")
        raise AssertionError(f"Button with location ({row}, {column}) not found on the inline keyboard.")