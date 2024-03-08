from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import User, TelegramObject

from database.orm_queries import orm_select_user_by_telegram_id

from config_data.config import Config

from sqlalchemy.ext.asyncio import async_sessionmaker

class UserMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
        ) -> Any:
        config: Config = data["config"]
        from_user: User = data["event_from_user"]
        if from_user.id in config.bot.admins:
            result = await handler(event, data)
            return result

        async with self.session_pool() as session:
            data['session'] = session
            user_id = await orm_select_user_by_telegram_id(
                session,
                telegram_id=from_user.id)
            if user_id:
                result = await handler(event, data)
                return result
            else:
                await event.answer(
                        text="<b>You are not registered</b>", # TODO: Implement registration process
                        # reply_markup=reply_markup,
                    )