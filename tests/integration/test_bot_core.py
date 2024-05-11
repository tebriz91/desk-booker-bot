import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import TYPE_CHECKING
from datetime import datetime
import pytest
from unittest.mock import patch, AsyncMock
from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from aiogram_dialog.test_tools import MockMessageManager, BotClient
from aiogram_dialog.test_tools.keyboard import InlineButtonTextLocator, InlineButtonPositionLocator
from fluentogram import TranslatorRunner # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession

from tests.integration.mocked_bot import MockedBot
from tests.utils.utils_integration import (
    TEST_USERS,
    TEST_ROOMS,
    TEST_DESKS,
    safe_insert,
)
from app.config_data.config import Config
from app.services.user.dates_generator import generate_dates
from app.services.common.rooms_list_generator import (
    generate_available_rooms_list,
    generate_available_rooms_as_list_of_tuples,
)
from app.services.common.room_plan_getter import get_room_plan_by_room_name
from app.services.common.desks_list_generator import generate_desks_list
from app.services.bookings_list_generator import (
    generate_current_bookings_by_telegram_id,
    generate_current_bookings_list_by_room_id,
)
from app.database.models import User
from app.database.orm_queries import (
    orm_insert_users,
    orm_insert_rooms,
    orm_insert_desks_by_room_name,
    # orm_delete_booking_by_id,
    orm_select_booking_by_telegram_id_and_date_selectinload,
    orm_select_booking_by_id,
)

if TYPE_CHECKING:
    from app.locales.stub import TranslatorRunner # type: ignore

from app.utils.logger import Logger
logger = Logger()


@pytest.mark.asyncio
async def test_booking_dialog(
    i18n: TranslatorRunner,
    user_client: BotClient,
    bot: MockedBot,
    dp: Dispatcher,
    message_manager: MockMessageManager,
    config: Config,
    session: AsyncSession,
):
    logger.info("Test of booking_dialog started.")
    
    #* TEST DATA SETUP
    
    async with session.begin():
        if not await safe_insert(session, orm_insert_users, data=TEST_USERS, entity_name="users"):
            return  # Exit if unable to add users

        if await safe_insert(session, orm_insert_rooms, data=TEST_ROOMS, entity_name="rooms"):
            await safe_insert(session, orm_insert_desks_by_room_name, data=TEST_DESKS, entity_name="desks")
    
    logger.info(f"Setting up test user with ID: {TEST_USERS[0][0]} and name: {TEST_USERS[0][1]}.")
    telegram_id: int = TEST_USERS[0][0]
    user_client = BotClient(dp, user_id=telegram_id)
    
    message_manager.reset_history() # Reset the message manager history. This is necessary to avoid interference from previous tests.
    
    logger.info("Sending '/book' command.")
    await user_client.send(text="/book")
    
    #* DATE SELECTION
    
    date_selection_message = message_manager.one_message()
    
    assert date_selection_message.text == i18n.select.date()
    logger.info("Message text:\n")
    logger.info(f"{date_selection_message.text}\n")
    logger.info("... matches expected text:\n")
    logger.info(f"{i18n.select.date()}\n")
    
    logger.info("Generating dates using generate_dates function.")
    dates = await generate_dates(
        config.bot_operation.num_days,
        config.bot_operation.exclude_weekends,
        config.bot_operation.timezone,
        config.bot_operation.country_code,
        config.bot_operation.date_format,
    )
    
    assert len(dates) == config.bot_operation.num_days
    logger.info(f"Number of dates generated: {len(dates)} equals to config num_days: {config.bot_operation.num_days}")
        
    # Loop through each date and its corresponding button
    for i, date in enumerate(dates):
        # Access the button text for the current date
        button_text = date_selection_message.reply_markup.inline_keyboard[i][0].text  # type: ignore
        # Check if the date is in the button text
        assert date in button_text
        logger.info(f"Date: {date} matches button text: {button_text}")
    
    logger.info("Listing all available buttons on UI:")
    for i, row in enumerate(date_selection_message.reply_markup.inline_keyboard): # type: ignore
        for j, button in enumerate(row):
            logger.info(f"Button at ({i},{j}): '{button.text}'")
    
    first_date_button = date_selection_message.reply_markup.inline_keyboard[0][0].text # type: ignore
    
    logger.info(f"Attempting to click on the first date button: {first_date_button}")
    try:
        message_manager.reset_history()
        date_button_callback_id = await user_client.click(date_selection_message, InlineButtonPositionLocator(0, 0))
        logger.info("Button click simulated successfully.")
    except ValueError as e:
        logger.error(f"Failed to simulate button click: {e}")
        detailed_buttons = "\n".join([f"Button at ({i},{j}): '{btn.text}'" for i, row in enumerate(date_selection_message.reply_markup.inline_keyboard) for j, btn in enumerate(row)]) # type: ignore
        logger.debug(f"Failed to find button. Available buttons:\n{detailed_buttons}")
        raise AssertionError(f"Button with the text '{first_date_button}' was not found.")

    message_manager.assert_answered(date_button_callback_id)
    logger.info(f"Callback message has been answered. Callback ID: {date_button_callback_id}")

    room_selection_message = message_manager.one_message()
    
    expected_text = f"{i18n.selected.date(date=first_date_button)}\n{i18n.select.room()}"
    
    assert room_selection_message.text == expected_text
    logger.info(
        "Message text:\n\n"
        f"{room_selection_message.text}\n\n"
        "... matches expected text:\n\n"
        f"{expected_text}\n"
        )
    
    #* ROOM SELECTION
    
    logger.info("Getting room list with generate_available_rooms_list function...")
    rooms = await generate_available_rooms_list(session)
    logger.info(f"Available rooms: {rooms}")
    
    logger.info("Listing all available buttons on UI:")
    for i, row in enumerate(room_selection_message.reply_markup.inline_keyboard): # type: ignore
        for j, button in enumerate(row):
            logger.info(f"Button at ({i},{j}): '{button.text}'")
        
    logger.info("Checking if all rooms are represented on UI...")
    for room in rooms:
        assert any(room == btn.text for row in room_selection_message.reply_markup.inline_keyboard for btn in row), f"Room {room} not found in button texts" # type: ignore
    logger.info("All rooms have been correctly represented on UI.")
    
    first_room_button = room_selection_message.reply_markup.inline_keyboard[0][0].text # type: ignore
    
    logger.info("Getting room plan URL with get_room_plan_by_room_name function...")
    room_plan = await get_room_plan_by_room_name(session, first_room_button)
    
    logger.info(f"Attempting to click on the first room button: {first_room_button}")
    try:
        message_manager.reset_history()
        room_button_callback_id = await user_client.click(room_selection_message, InlineButtonPositionLocator(0, 0))
        logger.info("Button click simulated successfully.")
    except ValueError as e:
        logger.error(f"Failed to simulate button click: {e}")
    
    message_manager.assert_answered(room_button_callback_id)
    logger.info(f"Callback message has been answered. Callback ID: {room_button_callback_id}")

    desk_selection_message = message_manager.one_message()
    
    expected_text = f'{i18n.selected.date(date=first_date_button)}\n{i18n.selected.room(room_name=first_room_button)}<a href="{room_plan}">📋</a>\n{i18n.select.desk()}'
    
    assert desk_selection_message.text == expected_text
    logger.info(
        "Message text:\n\n"
        f"{desk_selection_message.text}\n\n"
        "... matches expected text:\n\n"
        f"{expected_text}\n"
        )
    
    #* DESK SELECTION
    
    logger.info("Getting desk list from generate_desk_list function...")
    desks = await generate_desks_list(
            session,
            room_name=first_room_button,
            date=first_date_button,
            date_format=str(config.bot_operation.date_format),
            telegram_id=telegram_id,
            advanced_mode=config.bot_operation.advanced_mode,
            standard_access_days=config.bot_advanced_mode.standard_access_days)
    logger.info(f"Available desks: {desks}")
    
    logger.info("Listing all available buttons on UI:")
    for i, row in enumerate(desk_selection_message.reply_markup.inline_keyboard): # type: ignore
        for j, button in enumerate(row):
            logger.info(f"Button at ({i},{j}): '{button.text}'")
    
    logger.info("Checking if all desks are represented on UI...")
    for desk in desks:
        assert any(desk == btn.text for row in desk_selection_message.reply_markup.inline_keyboard for btn in row), f"Desk {desk} not found in button texts" # type: ignore
    logger.info("All desks have been correctly represented on UI.")
    
    first_desk_button = desk_selection_message.reply_markup.inline_keyboard[0][0].text # type: ignore
    
    # Mocking the answer method in CallbackQuery
    with patch.object(CallbackQuery, 'answer', new_callable=AsyncMock) as mock_answer:
        
        expected_text = i18n.desk.booker.success(date=first_date_button, room_name=first_room_button, desk_name=first_desk_button)
        
        mock_answer.return_value = expected_text # Set return value for the mock
        
        try:
            logger.info(f"Attempting to click on the first desk button: {first_desk_button}")
            message_manager.reset_history()
            desk_button_callback_id = await user_client.click(desk_selection_message, InlineButtonPositionLocator(0, 0))
            logger.info("Button click simulated successfully.")
        except ValueError as e:
            logger.error(f"Failed to simulate button click: {e}")
        
        message_manager.assert_answered(desk_button_callback_id)
        logger.info(f"Callback message has been answered. Callback ID: {desk_button_callback_id}")
        
        mock_answer.assert_called_once_with(text=expected_text, show_alert=True)
        
        # Compare the expected and actual result after the interaction
        actual_text = mock_answer.call_args[1]['text']  # Retrieve the actual text passed to the answer method
        show_alert = mock_answer.call_args[1]['show_alert']  # Retrieve the 'show_alert' flag passed to the answer method
        
        if actual_text == expected_text:
            logger.info(
                "Callback message text:\n\n"
                f"{actual_text}\n\n"
                "... matches expected text:\n\n"
                f"{expected_text}\n"
                )
        else:
            logger.info("Mismatch in callback message text!")
            logger.info("Expected:\n")
            logger.info(f"{expected_text}\n")
            logger.info("Actual:\n")
            logger.info(f"{actual_text}\n")
            
        if show_alert:
            logger.info(f"Show alert flag is set to {show_alert}. Alert was displayed.")
        else:
            logger.info(f"Show alert flag is set to {show_alert}. Alert was not displayed.")

    #* CHECKING DATABASE RECORD

    logger.info("Checking the database for a booking record using orm_select_booking_by_telegram_id_and_date_selectinload...")
    booking_date = datetime.strptime(first_date_button, str(config.bot_operation.date_format))
    try:
        booking = await orm_select_booking_by_telegram_id_and_date_selectinload(
        session,
        telegram_id=telegram_id,
        booking_date=booking_date,
        )
    except Exception as e:
        logger.error(f"Failed to retrieve booking record: {e}")
        raise
    
    if booking is not None:
        logger.info(
            "Booking record from database:\n"
            f"Telegram name: @{booking.user.telegram_name}\n"
            f"Telegram ID: {booking.user.telegram_id}\n" 
            f"Booking date: {booking.date}\n" 
            f"Room: {booking.desk.room.name}\n"
            f"Desk: {booking.desk.name}\n"
            f"Booked at: {booking.created_at}\n"
            f"Booking ID: {booking.id}"
        )
    else:
        raise AssertionError("Booking record not found in the database.")
    
    # logger.info("Cleaning up the record using orm_delete_booking_by_id...")
    # try:
    #     await orm_delete_booking_by_id(session, booking.id)
    #     logger.info("Booking record has been successfully deleted.")
    # except Exception as e:
    #     logger.error(f"Failed to delete booking record: {e}")
    #     raise
    
    logger.info("Test of booking_dialog completed successfully.")


@pytest.mark.asyncio
async def test_all_bookings_dialog(
    i18n: TranslatorRunner,
    user_client: BotClient,
    bot: MockedBot,
    dp: Dispatcher,
    message_manager: MockMessageManager,
    config: Config,
    session: AsyncSession,
):
    logger.info("Test of all_bookings_dialog started.")
    logger.info(f"Setting up test user with ID: {TEST_USERS[0][0]} and name: {TEST_USERS[0][1]}.")
    telegram_id: int = TEST_USERS[0][0]
    user_client = BotClient(dp, user_id=telegram_id)
    
    message_manager.reset_history() # Reset the message manager history. This is necessary to avoid interference from previous tests.
    
    logger.info("Sending '/all_bookings' command.")
    await user_client.send(text="/all_bookings")
    
    #* ROOM SELECTION
    
    logger.info("Getting room list with generate_available_rooms_as_list_of_tuples function...")
    rooms = await generate_available_rooms_as_list_of_tuples(session) # Returns list of tuples with room_id and room_name
    logger.info(f"Available rooms:")
    for i, room in enumerate(rooms):
        logger.info(f"Room ID: {room[0]}, room name: {room[1]}")
    
    room_selection_message = None
    try:
        room_selection_message = message_manager.one_message()
    except AssertionError as e:
        logger.error("Expected exactly one message, but either none or multiple messages were captured.")
        if room_selection_message is not None:
            logger.error(f"Message text: {room_selection_message.text}")
        else:
            logger.error("No message was captured.")
        raise
    
    expected_message = i18n.select.room()
    
    assert room_selection_message.text == expected_message
    logger.info("Message text:\n")
    logger.info(f"{room_selection_message.text}\n")
    logger.info("... matches expected text:\n")
    logger.info(f"{expected_message}\n")
    
    logger.info("Listing all available buttons on UI:")
    for i, row in enumerate(room_selection_message.reply_markup.inline_keyboard): # type: ignore
        for j, button in enumerate(row):
            logger.info(f"Button at ({i},{j}): '{button.text}'")
            
    logger.info("Checking if all rooms are represented on UI...")
    for room in rooms:
        assert any(room[1] == btn.text for row in room_selection_message.reply_markup.inline_keyboard for btn in row), f"Room {room[1]} not found in button texts" # type: ignore
    logger.info("All rooms have been correctly represented on UI.")
    
    first_room_id = rooms[0][0]
    first_room_button = room_selection_message.reply_markup.inline_keyboard[0][0].text # type: ignore
    
    logger.info(f"Attempting to click on the first room button: {first_room_button}")
    try:
        message_manager.reset_history()
        room_button_callback_id = await user_client.click(room_selection_message, InlineButtonTextLocator(first_room_button))
        logger.info("Button click simulated successfully.")
    except ValueError as e:
        logger.error(f"Failed to simulate button click: {e}")
        
    message_manager.assert_answered(room_button_callback_id)
    logger.info(f"Callback message has been answered. Callback ID: {room_button_callback_id}")
    
    #* BOOKINGS LIST
    
    logger.info("Getting bookings list using generate_current_bookings_list_by_room_id...")
    bookings = await generate_current_bookings_list_by_room_id(
        i18n,
        session,
        date_format=str(config.bot_operation.date_format),
        date_format_short=str(config.bot_operation.date_format_short),
        room_id=first_room_id,
    ) # Returns a tuple of two strings: the first string a tag for the response, and the second string is the response message
    
    expected_message = bookings[1]
    
    bookings_list_message = None
    try:
        bookings_list_message = message_manager.one_message()
    except AssertionError as e:
        logger.error("Expected exactly one message, but either none or multiple messages were captured.")
        if bookings_list_message is not None:
            logger.error(f"Message text: {bookings_list_message.text}")
        else:
            logger.error("No message was captured.")
        raise
    
    assert bookings_list_message.text == expected_message
    
    logger.info("Message text:\n")
    logger.info(f"{bookings_list_message.text}")
    logger.info("... matches expected text:\n")
    logger.info(f"{expected_message}")
    
    #* EXIT BUTTON
    
    logger.info("Listing all available buttons on UI:")
    for i, row in enumerate(bookings_list_message.reply_markup.inline_keyboard): # type: ignore
        for j, button in enumerate(row):
            logger.info(f"Button at ({i},{j}): '{button.text}'")
    
    button_exit_text = i18n.button.exit()
    
    logger.info("Checking if the exit button is represented on UI...")
    assert any(button_exit_text == btn.text for row in bookings_list_message.reply_markup.inline_keyboard for btn in row), f"Exit button: {button_exit_text} not found in button texts" # type: ignore
    
    logger.info("Attempting to click on the exit button.")
    try:
        message_manager.reset_history()
        exit_button_callback_id = await user_client.click(bookings_list_message, InlineButtonTextLocator(button_exit_text))
        logger.info("Button click simulated successfully.")
    except ValueError as e:
        logger.error(f"Failed to simulate button click: {e}")
        
    message_manager.assert_answered(exit_button_callback_id)
    logger.info(f"Callback message has been answered. Callback ID: {exit_button_callback_id}")
    
    logger.info("Test of all_bookings_dialog completed successfully.")


@pytest.mark.asyncio
async def test_cancel_bookings_dialog(
    i18n: TranslatorRunner,
    user_client: BotClient,
    bot: MockedBot,
    dp: Dispatcher,
    message_manager: MockMessageManager,
    config: Config,
    session: AsyncSession,
):
    logger.info("Test of cancel_bookings_dialog started.")
    logger.info(f"Setting up test user with ID: {TEST_USERS[0][0]} and name: {TEST_USERS[0][1]}.")
    telegram_id: int = TEST_USERS[0][0]
    user_client = BotClient(dp, user_id=telegram_id)
    
    message_manager.reset_history() # Reset the message manager history. This is necessary to avoid interference from previous tests.
    
    logger.info("Sending '/cancel' command.")
    await user_client.send(text="/cancel")
    
    booking_selection_message = None
    try:
        booking_selection_message = message_manager.one_message()
    except AssertionError as e:
        logger.error("Expected exactly one message, but either none or multiple messages were captured.")
        if booking_selection_message is not None:
            logger.error(f"Message text: {booking_selection_message.text}")
        else:
            logger.error("No message was captured.")
        raise
    
    expected_message = i18n.select.booking.to.cancel()
    
    assert booking_selection_message.text == expected_message
    logger.info("Message text:\n")
    logger.info(f"{booking_selection_message.text}\n")
    logger.info("... matches expected text:\n")
    logger.info(f"{expected_message}\n")
    
    logger.info("Getting bookings list using generate_current_bookings_by_telegram_id function...")
    bookings = await generate_current_bookings_by_telegram_id(
        i18n,
        session,
        date_format=str(config.bot_operation.date_format),
        telegram_id=telegram_id,
    )
    if isinstance(bookings, str):
        raise AssertionError(f"Failed to get bookings list: {bookings}")
    if not bookings:
        raise AssertionError("No bookings found.")
    if bookings:
        # Remove booking ID from the list of bookings and return the list of booking data in readable format
        logger.info("Available bookings:")
        for i, booking in enumerate(bookings):
            logger.info(f"Booking {i+1}: {booking[1]}")
            
    logger.info("Listing all available buttons on UI:")
    for i, row in enumerate(booking_selection_message.reply_markup.inline_keyboard): # type: ignore
        for j, button in enumerate(row):
            logger.info(f"Button at ({i},{j}): '{button.text}'")
            
    logger.info("Checking if all bookings are represented on UI...")
    for booking in bookings:
        assert any(booking[1] == btn.text for row in booking_selection_message.reply_markup.inline_keyboard for btn in row), f"Booking {booking[1]} not found in button texts" # type: ignore
    logger.info("All bookings have been correctly represented on UI.")
    
    first_booking_id = bookings[0][0]
    
    first_booking_button = booking_selection_message.reply_markup.inline_keyboard[0][0].text # type: ignore
    
    # Mocking the answer method in CallbackQuery
    with patch.object(CallbackQuery, 'answer', new_callable=AsyncMock) as mock_answer:
        
        expected_text = i18n.cancel.booking.success()
        
        mock_answer.return_value = expected_text
        
        try:
            logger.info(f"Attempting to click on the first booking button: {first_booking_button}")
            message_manager.reset_history()
            booking_button_callback_id = await user_client.click(booking_selection_message, InlineButtonPositionLocator(0, 0))
            logger.info("Button click simulated successfully.")
        except ValueError as e:
            logger.error(f"Failed to simulate button click: {e}")
            
        message_manager.assert_answered(booking_button_callback_id)
        logger.info(f"Callback message has been answered. Callback ID: {booking_button_callback_id}")
        
        mock_answer.assert_called_once_with(text=expected_text)
        
        actual_text = mock_answer.call_args[1]['text']
        
        if actual_text == expected_text:
            logger.info("Callback message text:\n")
            logger.info(f"{actual_text}\n")
            logger.info("... matches expected text:\n")
            logger.info(f"{expected_text}\n")
        else:
            logger.info("Mismatch in callback message text!")
            logger.info("Expected:\n")
            logger.info(f"{expected_text}\n")
            logger.info("Actual:\n")
            logger.info(f"{actual_text}\n")
        
    #* CHECKING DATABASE RECORD

    logger.info("Checking the database for a booking record using orm_select_booking_by_id...")
    try:
        booking_obj = await orm_select_booking_by_id(
        session,
        booking_id=first_booking_id,
        )
    except Exception as e:
        logger.error(f"Failed to retrieve booking record: {e}")
        raise
    
    if booking_obj is None:
        logger.info("Booking record not found in the database.")
    
    if booking_obj is not None:
        logger.error("Booking record was not deleted.")
        logger.info(
            "Booking record from database:\n"
            f"Booking ID: {booking_obj.id}"
            f"Booking date: {booking_obj.date}\n"
            f"Telegram ID: {booking_obj.telegram_id}\n"
            f"Desk ID: {booking_obj.desk_id}\n"
            f"Booked at: {booking_obj.created_at}\n"
        )

    logger.info("Test of cancel_bookings_dialog completed successfully.")