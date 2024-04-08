from typing import TYPE_CHECKING

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select
from aiogram.types import CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from states.states import Booking

from services.user.booking_checker import check_existing_booking
from services.user.desk_assignment_checker import check_desk_assignment
from services.common.room_plan_getter import get_room_plan_by_room_name
from services.common.desks_list_generator import generate_desks_list
from services.user.desk_booker import desk_booker
from database.orm_queries import DeskBookerError

from utils.logger import Logger

if TYPE_CHECKING:
    from locales.stub import TranslatorRunner

logger = Logger()


async def selected_date(query: CallbackQuery,
                        widget: Select,
                        dialog_manager: DialogManager,
                        item_id: str,
                        ) -> None:
    """
    Handle the selection of a date in the booking dialog.

    Args:
        query (CallbackQuery): The callback query object.
        widget (Select): The select widget.
        dialog_manager (DialogManager): The dialog manager.
        item_id (str): The selected date.

    Returns:
        None
    """
    # Get TranslatorRunner from i18n middleware
    i18n: TranslatorRunner = dialog_manager.middleware_data['i18n']
    # Get session from DataBaseSession middleware
    session: AsyncSession = dialog_manager.middleware_data['session']
    # Get the selected date
    date = item_id
    # Get the bot operation configuration
    config = dialog_manager.start_data['bot_operation_config']
    # Get the date format from the configuration
    date_format = str(config['date_format'])
    # Get telegram_id from callback query
    telegram_id = query.from_user.id
    # Get the existing booking for the selected date, if any
    existing_booking = await check_existing_booking(
                                            i18n,
                                            session,
                                            telegram_id,
                                            date,
                                            date_format)
    try:
        # Answer user with the existing booking, if any
        if existing_booking:
            await query.answer(text=f"{existing_booking}", show_alert=True)
            await dialog_manager.switch_to(state=Booking.select_date)
            logger.info(f">>>>>>>>>>>>>existing_booking: {existing_booking}")
        # If no existing booking, check for desk assignment
        if not existing_booking:
            # Get the desk assignment for the selected date, if any
            desk_assignment = await check_desk_assignment(
                                            i18n,
                                            session,
                                            telegram_id,
                                            date,
                                            date_format)
            # Answer user with the desk assignment, if any
            if desk_assignment:
                await query.answer(text=f"{desk_assignment}", show_alert=True)
                await dialog_manager.switch_to(state=Booking.select_date)
                logger.info(f">>>>>>>>>>>>>desk_assignment: {desk_assignment}")
            else:
                # Save the selected date to the dialog data
                dialog_manager.dialog_data['date'] = date
                # Switch to the next window
                await dialog_manager.switch_to(Booking.select_room)
    except Exception as e:
        await query.message.edit_text(f"An error occurred: {e}")
        await dialog_manager.done()


async def selected_room(query: CallbackQuery,
                        widget: Select,
                        dialog_manager: DialogManager,
                        item_id: str,
                        ) -> None:
    """
    Handles the selection of a room in the booking process.

    Args:
        query (CallbackQuery): The callback query object.
        widget (Select): The select widget object.
        dialog_manager (DialogManager): The dialog manager object.
        item_id (str): The name of the selected room.

    Returns:
        None
    """
    # Get TranslatorRunner from i18n middleware
    i18n: TranslatorRunner = dialog_manager.middleware_data['i18n']
    # Get session from DataBaseSession middleware
    session: AsyncSession = dialog_manager.middleware_data['session']
    # Save the selected room to the dialog data
    dialog_manager.dialog_data['room_name'] = item_id
    # Get the selected date from the dialog data
    room_name = dialog_manager.dialog_data['room_name']
    # Get the selected date from the dialog data
    date = dialog_manager.dialog_data['date']
    # Get telegram_id from callback query
    telegram_id = query.from_user.id
    # Get the bot operation configuration
    c_ops = dialog_manager.start_data['bot_operation_config']
    # Get the bot advanced mode configuration
    c_adv = dialog_manager.start_data['bot_advanced_mode_config']
    # Get the date format from the configuration
    date_format = str(c_ops['date_format'])
    # Get the advanced mode (boolean value) from the configuration
    advanced_mode = bool(c_ops['advanced_mode'])
    # Get room_plan from the database
    room_plan_url = await get_room_plan_by_room_name(session, room_name)
    # Save room_plan_url to the dialog data
    dialog_manager.dialog_data['room_plan_url'] = room_plan_url
    try:
        # If advanced mode is enabled, get standard access days number
        standard_access_days = int(c_adv['standard_access_days']) if advanced_mode else None
        # Generate a list of available, not booked desks for the selected date and room, considering the standard access days if advanced mode is enabled
        desks = await generate_desks_list(
            session,
            room_name,
            date,
            date_format,
            advanced_mode,
            telegram_id,
            standard_access_days)
    except Exception as e:
        await query.message.edit_text(f"An error occurred: {e} while retrieving available desks. Please try again later.")
        await dialog_manager.done()
    
    try:
        # Answer user if desks is a string (error message)
        if isinstance(desks, str):
            await query.message.edit_text(text=f"{desks}")
            await dialog_manager.done()
        # Answer user is desks is a empty list
        if isinstance(desks, list) and not desks:
            #! there-are-no-desks
            await query.answer(text=i18n.there.are.no.desks(room_name=room_name, date=date), show_alert=True)
            await dialog_manager.switch_to(Booking.select_date)
        # Save rooms to dialog_data and switch to the next window if desks is a list and not empty
        if isinstance(desks, list) and desks:
            dialog_manager.dialog_data['desks'] = desks
            await dialog_manager.switch_to(Booking.select_desk)
    except Exception as e:
        await query.message.edit_text(f"An error occurred: {e} while processing available desks. Please try again later.")
        await dialog_manager.done()


async def selected_desk(query: CallbackQuery,
                        widget: Select,
                        dialog_manager: DialogManager,
                        item_id: str,
                        ) -> None:
    """
    Handles the selection of a desk in the booking dialog.

    Args:
        query (CallbackQuery): The callback query object.
        widget (Select): The select widget containing the available desks.
        dialog_manager (DialogManager): The dialog manager instance.
        item_id (str): The name of the selected desk.

    Returns:
        None
    """
    # Get TranslatorRunner from i18n middleware
    i18n: TranslatorRunner = dialog_manager.middleware_data['i18n']
    # Get session from DataBaseSession middleware
    session: AsyncSession = dialog_manager.middleware_data['session']
    # Save the selected desk to the dialog data
    dialog_manager.dialog_data['desk_name'] = item_id
    # Get the selected desk from the dialog data
    desk_name = dialog_manager.dialog_data['desk_name']
    # Get the selected room from the dialog data
    room_name = dialog_manager.dialog_data['room_name']
    # Get the selected date from the dialog data
    date = dialog_manager.dialog_data['date']
    # Get telegram_id from callback query
    telegram_id = query.from_user.id
    # Get the bot operation configuration
    config = dialog_manager.start_data['bot_operation_config']
    # Get the date format from the configuration
    date_format = str(config['date_format'])
    try:
        # Insert the booking into the database
        result = await desk_booker(
            i18n,
            session,
            telegram_id,
            desk_name,
            room_name,
            date,
            date_format,
        )
        # Answer user with the booking result
        await query.answer(text=f"{result}", show_alert=True)
        await dialog_manager.switch_to(Booking.select_date)
    except DeskBookerError as e:
        # In case of a race condition, answer user with the DeskBookerError message and switch to the select_room window
        await query.answer(text=f"{e}", show_alert=True)
        await dialog_manager.switch_to(Booking.select_room)
    except Exception as e:
        await query.message.edit_text(f"An error occurred: {e} while processing the booking. Please try again later.")
        await dialog_manager.done()