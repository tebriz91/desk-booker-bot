import random
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
from tests.integration.utils import (
    TEST_USERS_1, TEST_ROOMS_1, TEST_DESKS_1,
    TEST_USERS_2, TEST_ROOMS_2, TEST_DESKS_2,
    TEST_USERS_3, TEST_ROOMS_3, TEST_DESKS_3,
    safe_insert,
    create_db,
    truncate_db_cascade,
)
from tests.integration.config import Config
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
logger = Logger(level=20)


test_data_sets = [
    (TEST_USERS_1, TEST_ROOMS_1, TEST_DESKS_1),
    (TEST_USERS_2, TEST_ROOMS_2, TEST_DESKS_2),
    (TEST_USERS_3, TEST_ROOMS_3, TEST_DESKS_3),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("test_data", test_data_sets)
async def test_all_dialogs(
    test_data,
    engine,
    i18n: TranslatorRunner,
    user_client: BotClient,
    bot: MockedBot,
    dp: Dispatcher,
    message_manager: MockMessageManager,
    config: Config,
    session: AsyncSession
    ):
    """ Integration test for all dialogs parametrized with different data sets. 
    
    The test runs through the following dialogs in sequence and each run is parametrized with a single data set taken from the test_data_sets list.
    """
    logger.info("Unpacking data set with test users, rooms, and desks...")
    test_users, test_rooms, test_desks = test_data
    
    logger.info("Test of booking_dialog started.")
    await booking_dialog(test_users, test_rooms, test_desks, engine, i18n, user_client, bot, dp, message_manager, config, session)
    
    logger.info("Test of booking_dialog_random_desk started.")
    await booking_dialog_random_desk(test_users, i18n, user_client, bot, dp, message_manager, config, session)
    
    logger.info("Test of all_bookings_dialog started.")
    await all_bookings_dialog(test_users, i18n, user_client, bot, dp, message_manager, config, session)
    
    logger.info("Test of cancel_bookings_dialog started.")
    await cancel_bookings_dialog(test_users, i18n, user_client, bot, dp, message_manager, config, session)


async def booking_dialog(
    test_users,
    test_rooms,
    test_desks,
    engine,
    i18n: TranslatorRunner,
    user_client: BotClient,
    bot: MockedBot,
    dp: Dispatcher,
    message_manager: MockMessageManager,
    config: Config,
    session: AsyncSession,
):
    c = config.bot_operation
    ca = config.bot_advanced_mode
    logger.debug("Bot configuration:")
    logger.debug(f"Advanced Mode: {c.advanced_mode}")
    logger.debug(f"Operation Days (num_days): {c.num_days}")
    logger.debug(f"Exclude Weekends: {c.exclude_weekends}")
    logger.debug(f"Timezone: {c.timezone}")
    logger.debug(f"Country code: {c.country_code}")
    logger.debug(f"Date format: {c.date_format}")
    logger.debug(f"Date format short: {c.date_format_short}")
    logger.debug(f"Standard Access Days: {ca.standard_access_days}")

    #* DATABASE SETUP
    
    logger.debug("Creating database tables, if they do not exist...")
    await create_db(engine)

    logger.debug("Truncating database tables...")
    await truncate_db_cascade(session)
    
    logger.info(f"Test users: {test_users}")
    
    logger.debug("Adding test data to the database...")
    async with session.begin():
        if not await safe_insert(
            session,
            orm_insert_users,
            test_users,
            "users"):
            return
        
    async with session.begin():
        if not await safe_insert(
            session,
            orm_insert_rooms,
            test_rooms,
            "rooms"):
            return
        
    async with session.begin():
        if not await safe_insert(
            session,
            orm_insert_desks_by_room_name,
            test_desks,
            "desks"):
            return
    
    logger.info(f"Setting up test user with ID: {test_users[0][0]} and name: {test_users[0][1]}.")
    telegram_id: int = test_users[0][0]
    user_client = BotClient(
        dp,
        user_id=telegram_id,
        chat_id=telegram_id)
    
    message_manager.reset_history() # Reset the message manager history. This is necessary to avoid interference from previous tests.
    
    logger.debug(f"Checkpoint 1. Number of sent messages: {len(message_manager.sent_messages)}")
    for msg in message_manager.sent_messages:
        logger.debug(f"Message content: {msg.text}")
    
    logger.info("Sending '/book' command.")
    await user_client.send(text="/book")
    
    #* DATE SELECTION
    
    messages = message_manager.sent_messages
    if not messages:
        logger.error(f"No messages were captured, expected at least one. Messages: {messages}.")
        assert False, "Expected at least one message but got none."
    elif len(messages) > 1:
        logger.error("Expected one message but multiple were captured.")
        for msg in messages:
            logger.debug(f"Captured message: {msg.text}")
        assert False, "Expected one message but multiple were captured."
    else:
        date_selection_message = messages[0]
        logger.debug(f"Checkpoint 2. Number of sent messages: {len(message_manager.sent_messages)}")
        for msg in message_manager.sent_messages:
            logger.debug(f"Message content: {msg.text}")
        expected_message = i18n.select.date()
        assert date_selection_message.text == expected_message, f"Expected text: {expected_message}, but got: {date_selection_message.text}"
    
    logger.info("Message text:\n")
    logger.info(f"{date_selection_message.text}\n")
    logger.info("... matches expected text:\n")
    logger.info(f"{i18n.select.date()}\n")
    
    logger.debug("Generating dates using generate_dates function.")
    dates = await generate_dates(
        c.num_days,
        c.exclude_weekends,
        c.timezone,
        c.country_code,
        c.date_format,
    )
    
    assert len(dates) == c.num_days
    logger.info(f"Number of dates generated: {len(dates)} equals to config num_days: {c.num_days}")
        
    # Loop through each date and its corresponding button
    for i, date in enumerate(dates):
        # Access the button text for the current date
        button_text = date_selection_message.reply_markup.inline_keyboard[i][0].text  # type: ignore
        # Check if the date is in the button text
        assert date in button_text
        logger.debug(f"Date: {date} matches button text: {button_text}")
    
    logger.debug("Listing all available buttons on UI:")
    for i, row in enumerate(date_selection_message.reply_markup.inline_keyboard): # type: ignore
        for j, button in enumerate(row):
            logger.debug(f"Button at ({i},{j}): '{button.text}'")
    
    first_date_button = date_selection_message.reply_markup.inline_keyboard[0][0].text # type: ignore
    
    logger.debug(f"Checkpoint 3. Number of sent messages: {len(message_manager.sent_messages)}")
    for msg in message_manager.sent_messages:
        logger.debug(f"Message content: {msg.text}")
    
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
    logger.debug(f"Callback message has been answered. Callback ID: {date_button_callback_id}")

    logger.debug(f"Checkpoint 4. Number of sent messages: {len(message_manager.sent_messages)}")
    for msg in message_manager.sent_messages:
        logger.debug(f"Message content: {msg.text}")

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
    
    logger.debug("Getting room list with generate_available_rooms_list function...")
    rooms = await generate_available_rooms_list(session)
    logger.debug(f"Available rooms: {rooms}")
    
    logger.debug("Listing all available buttons on UI:")
    for i, row in enumerate(room_selection_message.reply_markup.inline_keyboard): # type: ignore
        for j, button in enumerate(row):
            logger.debug(f"Button at ({i},{j}): '{button.text}'")
        
    logger.debug("Checking if all rooms are represented on UI...")
    for room in rooms:
        assert any(room == btn.text for row in room_selection_message.reply_markup.inline_keyboard for btn in row), f"Room {room} not found in button texts" # type: ignore
    logger.debug("All rooms have been correctly represented on UI.")
    
    logger.debug(f"Checkpoint 5. Number of sent messages: {len(message_manager.sent_messages)}")
    for msg in message_manager.sent_messages:
        logger.debug(f"Message content: {msg.text}")
    
    first_room_button = room_selection_message.reply_markup.inline_keyboard[0][0].text # type: ignore
    
    logger.debug("Getting room plan URL with get_room_plan_by_room_name function...")
    room_plan = await get_room_plan_by_room_name(session, first_room_button)
    
    logger.info(f"Attempting to click on the first room button: {first_room_button}")
    try:
        message_manager.reset_history()
        room_button_callback_id = await user_client.click(room_selection_message, InlineButtonPositionLocator(0, 0))
        logger.debug("Button click simulated successfully.")
    except ValueError as e:
        logger.error(f"Failed to simulate button click: {e}")
    
    message_manager.assert_answered(room_button_callback_id)
    logger.debug(f"Callback message has been answered. Callback ID: {room_button_callback_id}")

    logger.debug(f"Checkpoint 6. Number of sent messages: {len(message_manager.sent_messages)}")
    for msg in message_manager.sent_messages:
        logger.debug(f"Message content: {msg.text}")

    desk_selection_message = message_manager.one_message()
    
    expected_text = f'{i18n.selected.date(date=first_date_button)}\n{i18n.selected.room(room_name=first_room_button)}<a href="{room_plan}">📋</a>\n{i18n.select.desk()}'
    
    assert desk_selection_message.text == expected_text
    logger.info("Message text:\n")
    logger.info(f"{desk_selection_message.text}\n")
    logger.info("... matches expected text:\n")
    logger.info(f"{expected_text}\n")
    
    #* DESK SELECTION
    
    logger.debug("Getting desk list from generate_desk_list function...")
    desks = await generate_desks_list(
            session,
            room_name=first_room_button,
            date=first_date_button,
            date_format=str(config.bot_operation.date_format),
            telegram_id=telegram_id,
            advanced_mode=config.bot_operation.advanced_mode,
            standard_access_days=config.bot_advanced_mode.standard_access_days)
    logger.debug(f"Available desks: {desks}")
    
    logger.debug("Listing all available buttons on UI:")
    for i, row in enumerate(desk_selection_message.reply_markup.inline_keyboard): # type: ignore
        for j, button in enumerate(row):
            logger.debug(f"Button at ({i},{j}): '{button.text}'")
    
    logger.debug("Checking if all desks are represented on UI...")
    for desk in desks:
        assert any(desk == btn.text for row in desk_selection_message.reply_markup.inline_keyboard for btn in row), f"Desk {desk} not found in button texts" # type: ignore
    logger.debug("All desks have been correctly represented on UI.")
    
    first_desk_button = desk_selection_message.reply_markup.inline_keyboard[0][0].text # type: ignore
    
    logger.debug(f"Checkpoint 7. Number of sent messages: {len(message_manager.sent_messages)}")
    for msg in message_manager.sent_messages:
        logger.debug(f"Message content: {msg.text}")
    
    # Mocking the answer method in CallbackQuery
    with patch.object(CallbackQuery, 'answer', new_callable=AsyncMock) as mock_answer:
        
        expected_text = i18n.desk.booker.success(date=first_date_button, room_name=first_room_button, desk_name=first_desk_button)
        
        mock_answer.return_value = expected_text # Set return value for the mock
        
        try:
            logger.info(f"Attempting to click on the first desk button: {first_desk_button}")
            message_manager.reset_history()
            desk_button_callback_id = await user_client.click(desk_selection_message, InlineButtonPositionLocator(0, 0))
            logger.debug("Button click simulated successfully.")
        except ValueError as e:
            logger.error(f"Failed to simulate button click: {e}")
        
        message_manager.assert_answered(desk_button_callback_id)
        logger.debug(f"Callback message has been answered. Callback ID: {desk_button_callback_id}")
        
        mock_answer.assert_called_once_with(text=expected_text, show_alert=True)

        logger.debug(f"Checkpoint 8. Number of sent messages: {len(message_manager.sent_messages)}")
        for msg in message_manager.sent_messages:
            logger.debug(f"Message content: {msg.text}")

        # Compare the expected and actual result after the interaction
        actual_text = mock_answer.call_args[1]['text']  # Retrieve the actual text passed to the answer method
        show_alert = mock_answer.call_args[1]['show_alert']  # Retrieve the 'show_alert' flag passed to the answer method
        
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
            
        if show_alert:
            logger.info(f"Show alert flag is set to {show_alert}. Alert was displayed.")
        else:
            logger.error(f"Show alert flag is set to {show_alert}. Alert was not displayed.")

    #* CHECKING DATABASE RECORD

    logger.debug("Checking the database for a booking record using orm_select_booking_by_telegram_id_and_date_selectinload...")
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
    pass


async def booking_dialog_random_desk(
    test_users,
    i18n: TranslatorRunner,
    user_client: BotClient,
    bot: MockedBot,
    dp: Dispatcher,
    message_manager: MockMessageManager,
    config: Config,
    session: AsyncSession,
):
    logger.debug("Setting up test users:")
    
    logger.info(f"Test users: {test_users}")
    # Iterating through the test users starting from the second user and create a BotClient for each user, where user_id=telegram_id and chat_id=telegram_id
    for user in test_users[1:]:
        logger.debug(f"User: {user[1]} with ID: {user[0]} is being set up.")
        test_user_1 = BotClient(
            dp,
            user_id=user[0],
            chat_id=user[0])
        
        message_manager.reset_history()
        
        logger.info(f"User: {user[1]} is sending '/book' command.")
        await test_user_1.send(text="/book")
        
        date_selection_message = message_manager.one_message()
        
        # Get location of the random date button
        row: int = random.randint(0, int(config.bot_operation.num_days) - 1) # type: ignore
        column: int = 0
        
        logger.info(f"Attempting to click on random date button located at ({row},{column}).")
        try:
            message_manager.reset_history()
            rndm_date_btn_callback_id = await test_user_1.click(date_selection_message, InlineButtonPositionLocator(row, column))
        except ValueError as e:
            logger.error(f"Failed to simulate button click: {e}")
            raise
        
        message_manager.assert_answered(rndm_date_btn_callback_id)
        logger.debug(f"Callback message has been answered. Callback ID: {rndm_date_btn_callback_id}")
        
        room_selection_message = message_manager.one_message()
        rndm_desk_btn = i18n.booking.random.button()

        # Mocking the answer method in CallbackQuery
        with patch.object(CallbackQuery, 'answer', new_callable=AsyncMock) as mock_answer:
            
            logger.info("Attempting to click on random desk button.")
            try:
                message_manager.reset_history()
                rndm_desk_btn_callback_id = await test_user_1.click(room_selection_message, InlineButtonTextLocator(rndm_desk_btn))
            
                message_manager.assert_answered(rndm_desk_btn_callback_id)
                logger.debug(f"Callback message has been answered. Callback ID: {rndm_desk_btn_callback_id}")
                
                mock_answer.assert_called_once()
                assert mock_answer.call_args[1]['show_alert'] is True
                
                logger.info("Callback message text:\n")
                logger.info(f"{mock_answer.call_args[1]['text']}\n")
                logger.debug(f"Show alert flag is set to {mock_answer.call_args[1]['show_alert']}. Alert was displayed.\n")
            
            except ValueError as e:
                logger.error(f"Failed to simulate button click: {e}")
                raise
            
    logger.info("Test of test_booking_dialog_random_desk completed successfully.")
    pass

async def all_bookings_dialog(
    test_users,
    i18n: TranslatorRunner,
    user_client: BotClient,
    bot: MockedBot,
    dp: Dispatcher,
    message_manager: MockMessageManager,
    config: Config,
    session: AsyncSession,
):
    logger.info(f"Test users: {test_users}")
    
    logger.debug(f"Setting up test user with ID: {test_users[0][0]} and name: {test_users[0][1]}.")
    telegram_id: int = test_users[0][0]
    user_client = BotClient(
        dp,
        user_id=telegram_id,
        chat_id=telegram_id)
    
    message_manager.reset_history() # Reset the message manager history. This is necessary to avoid interference from previous tests.
    
    logger.info("Sending '/all_bookings' command.")
    await user_client.send(text="/all_bookings")
    
    #* ROOM SELECTION
    
    logger.debug("Getting room list with generate_available_rooms_as_list_of_tuples function...")
    rooms = await generate_available_rooms_as_list_of_tuples(session) # Returns list of tuples with room_id and room_name
    logger.debug(f"Available rooms:")
    for i, room in enumerate(rooms):
        logger.debug(f"Room ID: {room[0]}, room name: {room[1]}")
    
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
    
    logger.debug("Listing all available buttons on UI:")
    for i, row in enumerate(room_selection_message.reply_markup.inline_keyboard): # type: ignore
        for j, button in enumerate(row):
            logger.debug(f"Button at ({i},{j}): '{button.text}'")
            
    logger.debug("Checking if all rooms are represented on UI...")
    for room in rooms:
        assert any(room[1] == btn.text for row in room_selection_message.reply_markup.inline_keyboard for btn in row), f"Room {room[1]} not found in button texts" # type: ignore
    logger.debug("All rooms have been correctly represented on UI.")
    
    first_room_id = rooms[0][0]
    first_room_button = room_selection_message.reply_markup.inline_keyboard[0][0].text # type: ignore
    
    logger.info(f"Attempting to click on the first room button: {first_room_button}")
    try:
        message_manager.reset_history()
        room_button_callback_id = await user_client.click(room_selection_message, InlineButtonTextLocator(first_room_button))
        logger.debug("Button click simulated successfully.")
    except ValueError as e:
        logger.error(f"Failed to simulate button click: {e}")
        
    message_manager.assert_answered(room_button_callback_id)
    logger.info(f"Callback message has been answered. Callback ID: {room_button_callback_id}")
    
    #* BOOKINGS LIST
    
    logger.debug("Getting bookings list using generate_current_bookings_list_by_room_id...")
    bookings = await generate_current_bookings_list_by_room_id(
        i18n,
        session,
        date_format=str(config.bot_operation.date_format),
        date_format_short=str(config.bot_operation.date_format_short),
        room_id=first_room_id,
    )
    
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
    
    logger.debug("Listing all available buttons on UI:")
    for i, row in enumerate(bookings_list_message.reply_markup.inline_keyboard): # type: ignore
        for j, button in enumerate(row):
            logger.debug(f"Button at ({i},{j}): '{button.text}'")
    
    button_exit_text = i18n.button.exit()
    
    logger.debug("Checking if the exit button is represented on UI...")
    assert any(button_exit_text == btn.text for row in bookings_list_message.reply_markup.inline_keyboard for btn in row), f"Exit button: {button_exit_text} not found in button texts" # type: ignore
    
    logger.debug("Attempting to click on the exit button.")
    try:
        message_manager.reset_history()
        exit_button_callback_id = await user_client.click(bookings_list_message, InlineButtonTextLocator(button_exit_text))
        logger.debug("Button click simulated successfully.")
    except ValueError as e:
        logger.error(f"Failed to simulate button click: {e}")
        
    message_manager.assert_answered(exit_button_callback_id)
    logger.debug(f"Callback message has been answered. Callback ID: {exit_button_callback_id}")
    
    logger.info("Test of all_bookings_dialog completed successfully.")
    pass

async def cancel_bookings_dialog(
    test_users,
    i18n: TranslatorRunner,
    user_client: BotClient,
    bot: MockedBot,
    dp: Dispatcher,
    message_manager: MockMessageManager,
    config: Config,
    session: AsyncSession,
):
    logger.info(f"Test users: {test_users}")

    logger.debug(f"Setting up test user with ID: {test_users[0][0]} and name: {test_users[0][1]}.")
    telegram_id: int = test_users[0][0]
    user_client = BotClient(
        dp,
        user_id=telegram_id,
        chat_id=telegram_id)
    
    message_manager.reset_history() # Reset the message manager history. This is necessary to avoid interference from previous tests.
    
    logger.info("Sending '/cancel' command.")
    await user_client.send(text="/cancel")
    
    messages = message_manager.sent_messages
    if not messages:
        logger.error("No messages were captured, expected at least one.")
        assert False, "Expected at least one message but got none."
    elif len(messages) > 1:
        logger.error("Expected one message but multiple were captured.")
        for msg in messages:
            logger.debug(f"Captured message: {msg.text}")
        assert False, "Expected one message but multiple were captured."
    else:
        booking_selection_message = messages[0]
        logger.debug(f"Checkpoint 1. Number of sent messages: {len(messages)}")
        for msg in messages:
            logger.debug(f"Message content: {msg.text}")
        expected_message = i18n.select.booking.to.cancel()
        assert booking_selection_message.text == expected_message, f"Expected text: {expected_message}, but got: {booking_selection_message.text}"
    
    logger.info("Message text:\n")
    logger.info(f"{booking_selection_message.text}\n")
    logger.info("... matches expected text:\n")
    logger.info(f"{expected_message}\n")
    
    logger.debug("Getting bookings list using generate_current_bookings_by_telegram_id function...")
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
        logger.debug("Available bookings:")
        for i, booking in enumerate(bookings):
            logger.debug(f"Booking {i+1}: {booking[1]}")
            
    logger.debug("Listing all available buttons on UI:")
    for i, row in enumerate(booking_selection_message.reply_markup.inline_keyboard): # type: ignore
        for j, button in enumerate(row):
            logger.debug(f"Button at ({i},{j}): '{button.text}'")
            
    logger.debug("Checking if all bookings are represented on UI...")
    for booking in bookings:
        assert any(booking[1] == btn.text for row in booking_selection_message.reply_markup.inline_keyboard for btn in row), f"Booking {booking[1]} not found in button texts" # type: ignore
    logger.debug("All bookings have been correctly represented on UI.")
    
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
            logger.debug("Button click simulated successfully.")
        except ValueError as e:
            logger.error(f"Failed to simulate button click: {e}")
            
        message_manager.assert_answered(booking_button_callback_id)
        logger.debug(f"Callback message has been answered. Callback ID: {booking_button_callback_id}")
        
        mock_answer.assert_called_once_with(text=expected_text)
        
        actual_text = mock_answer.call_args[1]['text']
        
        if actual_text == expected_text:
            logger.info("Callback message text:\n")
            logger.info(f"{actual_text}\n")
            logger.info("... matches expected text:\n")
            logger.info(f"{expected_text}\n")
        else:
            logger.error("Mismatch in callback message text!")
            logger.error("Expected:\n")
            logger.error(f"{expected_text}\n")
            logger.error("Actual:\n")
            logger.error(f"{actual_text}\n")
        
    #* CHECKING DATABASE RECORD

    logger.debug("Checking the database for a booking record using orm_select_booking_by_id...")
    try:
        booking_obj = await orm_select_booking_by_id(
        session,
        booking_id=first_booking_id,
        )
    except Exception as e:
        logger.error(f"Failed to retrieve booking record: {e}")
        raise
    
    if booking_obj is None:
        logger.error("Booking record not found in the database.")
    
    if booking_obj is not None:
        logger.error("Booking record was not deleted.")
        logger.debug(
            "Booking record from database:\n"
            f"Booking ID: {booking_obj.id}"
            f"Booking date: {booking_obj.date}\n"
            f"Telegram ID: {booking_obj.telegram_id}\n"
            f"Desk ID: {booking_obj.desk_id}\n"
            f"Booked at: {booking_obj.created_at}\n"
        )

    logger.info("Test of cancel_bookings_dialog completed successfully.")
    
    #* TRUNCATE DATABASE TABLES
    
    logger.debug("Truncating database tables...")
    await truncate_db_cascade(session)
    pass