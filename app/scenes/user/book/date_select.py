from typing import Any, List

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.scene import Scene, on

from sqlalchemy.ext.asyncio import AsyncSession

from config_data.config import Config

from misc.const.button_labels import ButtonLabel
from keyboards.inline import get_inline_keyboard

from services.user.dates_generator import generate_dates
from services.user.booking_checker import check_existing_booking


class UserDateSelectScene(Scene, state="user_date_select_scene"):
    
    @on.message.enter()
    async def on_enter(self, message: Message, config: Config) -> Any:
        # Get the config data
        c = config.bot_operation
        # Generate dates
        dates: List[str] = await generate_dates(
            c.num_days,
            c.exclude_weekends,
            c.timezone,
            c.country_code,
            c.date_format)
        
        keyboard = get_inline_keyboard(
            buttons=dates,
            width=1,
            util_buttons=[
                ButtonLabel.EXIT.value,],
            width_util=1)
        
        await message.answer(
            text="Select date",
            reply_markup=keyboard)

    @on.callback_query.exit()
    async def on_exit(self, query: CallbackQuery) -> None:
        await self.wizard.clear_data()
        await query.message.edit_text(text='Process finished')
    
    @on.callback_query(F.data == ButtonLabel.EXIT.value)
    async def exit(self, query: CallbackQuery) -> None:
        await self.wizard.exit()
    
    @on.callback_query(F.data)
    async def on_date_select(self, query: CallbackQuery, session: AsyncSession, config: Config) -> None:
        date = query.data
        date_format = config.bot_operation.date_format
        # Call service to check if user has already has a booking on this date
        existing_booking = await check_existing_booking(
            session=session,
            telegram_id=query.from_user.id,
            date=date,
            date_format=date_format)
        try:
            if existing_booking is False:
                await query.message.edit_text(
                    text=f"Selected date: {date}. Proceeding to the room selection step...",
                    reply_markup=None)
                await self.wizard.goto("user_room_select_scene", session=session)
            else:
                await query.message.edit_text(
                    text=existing_booking,
                    reply_markup=None)
                await self.wizard.exit()
        except Exception as e:
            await query.message.edit_text(
                text=f"Error: {e}",
                reply_markup=None)
            await self.wizard.exit()