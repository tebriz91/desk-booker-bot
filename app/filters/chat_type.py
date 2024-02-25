"""
This module contains ChatType filter to filter messages by chat type. In simple terms, it is used to filter messages by the type of chat they are sent in. For example, you can use this filter to process only messages sent in private chats, or only in group chats, or only in channels, etc.
"""
import typing

from aiogram.filters import BaseFilter
from aiogram.types import Message


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: str | typing.Sequence[str]):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type