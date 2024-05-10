from datetime import datetime

from aiogram import Dispatcher
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Chat, Message, Update, User

from tests.integration.mocked_bot import MockedBot
from tests.utils.utils_core import MAIN_USER_ID

TEST_USER = User(
    id=MAIN_USER_ID,
    is_bot=False,
    first_name='Test'
)

TEST_CHAT = Chat(
    id=12,
    type='private',
    username=TEST_USER.username,
    first_name=TEST_USER.first_name,
    last_name=TEST_USER.last_name,
)

TEST_MESSAGE = Message(message_id=123, date=datetime.now(), chat=TEST_CHAT, text='')


def get_message(text: str, chat=TEST_CHAT, from_user=None, **kwargs) -> Message:
    """Create a message object for testing.

    Args:
        text (str): The text of the message.
        chat (Chat): The chat to associate with the message.
        from_user (User, optional): The user who sent the message.
        **kwargs: Additional message attributes.

    Returns:
        Message: A message object for testing.
    """
    return Message(
        message_id=123,
        date=datetime.now(),
        chat=chat,
        from_user=from_user,
        sender_chat=TEST_CHAT,
        text=text,
        **kwargs
    )


def get_chat(
    chat_id: int = None,
    chat_type: str = 'private',
    title: str = 'TEST_TITLE',
    username: str = TEST_CHAT.username,
    **kwargs
) -> Chat:
    """Create a chat object for testing.

    Args:
        chat_id (int, optional): The chat's unique identifier.
        chat_type (str, optional): The type of chat, e.g., 'private'.
        title (str, optional): The title of the chat.
        username (str): The username associated with the chat.
        **kwargs: Additional chat attributes.

    Returns:
        Chat: A chat object for testing.
    """
    return Chat(
        id=chat_id,
        type=chat_type,
        title=title,
        username=username,
        first_name=TEST_USER.first_name,
        last_name=TEST_USER.last_name,
        **kwargs
    )


def get_callback_query(
    data: str | CallbackData, from_user=None, message=None, **kwargs
) -> CallbackQuery:
    """Create a callback query object for testing.

    Args:
        data (str or CallbackData): The data associated with the query.
        from_user (User, optional): The user who sent the query.
        message (Message, optional): The message associated with the query.
        **kwargs: Additional callback query attributes.

    Returns:
        CallbackQuery: A callback query object for testing.
    """
    return CallbackQuery(
        id='test',
        from_user=from_user,
        chat_instance='test',
        message=message or TEST_MESSAGE,
        data=data,
        **kwargs
    )


def get_update(
    message: Message = None, callback_query: CallbackQuery = None, **kwargs
) -> Update:
    """Create a mocked update object for testing.

    Args:
        message (Message, optional): The message associated with the update.
        callback_query (CallbackQuery, optional): The callback query associated with
         the update.
        **kwargs: Additional update attributes.

    Returns:
        Update: A mocked update object for testing.
    """
    return Update(
        update_id=187,
        message=message,
        callback_query=callback_query,
        **kwargs
    )