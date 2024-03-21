from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import User, TelegramObject

from database.orm_queries import (
    orm_insert_user_to_waitlist,
    orm_select_user_by_telegram_id,
    orm_select_user_from_waitlist_by_telegram_id)

from config_data.config import Config

from sqlalchemy.ext.asyncio import async_sessionmaker

class UserMiddleware(BaseMiddleware):
    """
    This middleware checks if the user is registered in the database.
    """
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

        #  Check if the user is registered or if user is already in the process of registration (in the waitlist table)
        async with self.session_pool() as session:
            data['session'] = session
            user_id = await orm_select_user_by_telegram_id(
                session,
                telegram_id=from_user.id)
            if user_id:
                result = await handler(event, data)
                return result
            else:
                waitlist_user = await orm_select_user_from_waitlist_by_telegram_id(
                    session,
                    telegram_id=from_user.id)
                if not waitlist_user:
                    await orm_insert_user_to_waitlist(
                        session,
                        telegram_id=from_user.id,
                        telegram_name=from_user.username)
                    await event.answer(
                        text="You were added to the waitlist. Please wait for the admin to approve your registration.",
                        # reply_markup=reply_markup,
                    )
                else:
                    await event.answer(
                        text="You are already in the waitlist. Please wait for the admin to approve your registration.",
                        # reply_markup=reply_markup,
                    )