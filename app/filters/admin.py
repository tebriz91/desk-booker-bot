from typing import Union
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from app.config_data.config import Config

class AdminFilter(BaseFilter):
    is_admin: bool = True

    async def __call__(self, event: Union[Message, CallbackQuery], config: Config) -> bool:
        return (event.from_user.id in config.bot.admins) == self.is_admin