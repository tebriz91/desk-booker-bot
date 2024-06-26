from typing import TYPE_CHECKING

from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from fluentogram import TranslatorRunner # type: ignore

from app.routers.user.router import user_router
from app.config_data.config import Config
from app.services.bookings_list_generator import generate_list_of_current_bookings_by_telegram_id

if TYPE_CHECKING:
    from app.locales.stub import TranslatorRunner # type: ignore


@user_router.message(Command("my_bookings"))
async def process_command_my_bookings(message: Message,
                                      session: AsyncSession,
                                      config: Config,
                                      i18n: TranslatorRunner,
                                      ) -> None:
    c = config.bot_operation
    bookings = await generate_list_of_current_bookings_by_telegram_id(
        i18n,
        session,
        date_format=c.date_format,
        date_format_short=c.date_format_short,
        telegram_id=message.from_user.id,
        telegram_name=message.from_user.username)
    await message.answer(text=bookings)