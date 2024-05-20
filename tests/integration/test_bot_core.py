import random
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import TYPE_CHECKING, List, Tuple, Union
from datetime import datetime
import pytest
from unittest.mock import patch, AsyncMock
from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from aiogram_dialog.test_tools import MockMessageManager, BotClient
from fluentogram import TranslatorRunner # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from tests.integration.const import TEST_DATA
from tests.integration.utils import (
    log_bot_configuration,
    setup_db,
    truncate_db_cascade,
    assert_callback_answer,
    assert_inline_keyboard_buttons,
    click_inline_keyboard_button_by_location,
    click_inline_keyboard_button_by_text,
    log_inline_keyboard_buttons,
    assert_message_text,
    log_sent_messages,
)
from tests.integration.config import Config
from app.database.models import User, Room, Desk, Booking
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
    # orm_delete_booking_by_id,
    orm_select_booking_by_telegram_id_and_date_selectinload,
    orm_select_booking_by_id,
)

if TYPE_CHECKING:
    from app.locales.stub import TranslatorRunner # type: ignore

from app.utils.logger import Logger
logger = Logger(level=20)


@pytest.mark.asyncio
@pytest.mark.parametrize("TEST_DATA", TEST_DATA)
async def test_all_dialogs(
    TEST_DATA,
    engine: AsyncEngine,
    i18n: TranslatorRunner,
    dp: Dispatcher,
    message_manager: MockMessageManager,
    config: Config,
    session: AsyncSession
    ) -> None:
    """ Integration test for all dialogs parametrized with different data sets. 
    
    The test runs through the following dialogs in sequence and each run is parametrized with a single data set taken from the TEST_DATA list.
    
    Bot configuration is also parametrized in congig fixture in conftest.py.
    """
    logger.info("Unpacking data set with test users, rooms, and desks.")
    test_users, test_rooms, test_desks = TEST_DATA
    
    logger.info("Test of booking_dialog started.")
    await booking_dialog(test_users, test_rooms, test_desks, engine, i18n, dp, message_manager, config, session)
    
    logger.info("Test of booking_dialog_random_desk started.")
    await booking_dialog_random_desk(test_users, i18n, dp, message_manager, config)
    
    logger.info("Test of all_bookings_dialog started.")
    await all_bookings_dialog(test_users, i18n, dp, message_manager, config, session)
    
    logger.info("Test of cancel_bookings_dialog started.")
    await cancel_bookings_dialog(test_users, i18n, dp, message_manager, config, session)


async def booking_dialog(
    test_users: List[User],
    test_rooms: List[Room],
    test_desks: List[Desk],
    engine: AsyncEngine,
    i18n: TranslatorRunner,
    dp: Dispatcher,
    message_manager: MockMessageManager,
    config: Config,
    session: AsyncSession,
) -> None:
    c = config.bot_operation
    ca = config.bot_advanced_mode
    log_bot_configuration(config)
    
    #* DATABASE SETUP
    
    await setup_db(
        engine,
        session,
        test_users,
        test_rooms,
        test_desks,
    )
    
    # Retrieve the first test user
    user: User = test_users[0]
    
    logger.info(f"Setting up test user with ID: {user.telegram_id} and name: {user.telegram_name}.")
    telegram_id: int = user.telegram_id
    test_user = BotClient(
        dp,
        user_id=telegram_id,
        chat_id=telegram_id)
    
    message_manager.reset_history() # Reset the message manager history to avoid interference from previous tests.
    
    logger.info("Sending '/book' command.")
    await test_user.send(text="/book")
    
    #* DATE SELECTION
    
    if not message_manager.sent_messages:
        logger.error(f"No messages were captured, expected at least one. Messages: {message_manager.sent_messages}.")
        assert False, "Expected at least one message but got none."
    
    if len(message_manager.sent_messages) > 1:
        log_sent_messages(message_manager)
        assert False, "Expected one message but multiple were captured."
    
    if len(message_manager.sent_messages) == 1:
        date_selection_message = message_manager.sent_messages[0]
        assert_message_text(
            message=date_selection_message,
            expected_text=i18n.select.date())
    
    logger.debug("Generating dates.")
    dates: List[str] = await generate_dates(
        num_days=c.num_days,
        exclude_weekends=c.exclude_weekends,
        timezone=c.timezone,
        country_code=c.country_code,
        date_format=c.date_format,
    )
    
    assert len(dates) == c.num_days
    logger.info(f"Number of dates generated: {len(dates)} equals to config num_days: {c.num_days}")
    
    log_inline_keyboard_buttons(message=date_selection_message)
    
    logger.debug("Matching expected dates with buttons on UI.")
    assert_inline_keyboard_buttons(
        expected_texts=dates,
        message=date_selection_message)
    
    first_date_button = date_selection_message.reply_markup.inline_keyboard[0][0].text # type: ignore
    
    message_manager.reset_history()
    
    logger.info(f"Clicking on the first date button: {first_date_button}")
    date_button_callback_id = await click_inline_keyboard_button_by_location(
        test_user=test_user,
        message=date_selection_message,
        row=0,
        column=0,
    )
    
    message_manager.assert_answered(callback_id=date_button_callback_id)
    logger.debug(f"Callback message has been answered. Callback ID: {date_button_callback_id}")

    room_selection_message = message_manager.one_message()
    
    assert_message_text(
        message=room_selection_message,
        expected_text=f"{i18n.selected.date(date=first_date_button)}\n{i18n.select.room()}",
    )
    
    #* ROOM SELECTION
    
    logger.debug("Getting rooms list.")
    rooms: List[str] = await generate_available_rooms_list(session)
    
    log_inline_keyboard_buttons(room_selection_message)
        
    logger.debug("Matching expected rooms with buttons on UI.")
    assert_inline_keyboard_buttons(
        expected_texts=rooms,
        message=room_selection_message,
    )
    
    first_room_button = room_selection_message.reply_markup.inline_keyboard[0][0].text # type: ignore
    
    logger.debug("Getting room plan URL.")
    room_plan: str = await get_room_plan_by_room_name(
        session,
        room_name=first_room_button,
    )
    
    message_manager.reset_history()
    
    logger.info(f"Clicking on the first room button: {first_room_button}")
    room_button_callback_id = await click_inline_keyboard_button_by_location(
        test_user=test_user,
        message=room_selection_message,
        row=0,
        column=0,
    )
    
    message_manager.assert_answered(callback_id=room_button_callback_id)
    logger.debug(f"Callback message has been answered. Callback ID: {room_button_callback_id}")

    desk_selection_message = message_manager.one_message()
    
    assert_message_text(
        message=desk_selection_message,
        expected_text=f'{i18n.selected.date(date=first_date_button)}\n{i18n.selected.room(room_name=first_room_button)}<a href="{room_plan}">📋</a>\n{i18n.select.desk()}',
    )
    
    #* DESK SELECTION
    
    logger.debug("Getting desks list.")
    desks: List[str] | str = await generate_desks_list(
            session,
            room_name=first_room_button,
            date=first_date_button,
            date_format=str(c.date_format),
            telegram_id=telegram_id,
            advanced_mode=c.advanced_mode,
            standard_access_days=ca.standard_access_days)
    
    log_inline_keyboard_buttons(desk_selection_message)
    
    logger.debug("Matching expected desks with buttons on UI.")
    assert_inline_keyboard_buttons(
        expected_texts=desks,
        message=desk_selection_message,
    )
    
    first_desk_button = desk_selection_message.reply_markup.inline_keyboard[0][0].text # type: ignore
    
    # Mocking the answer method in CallbackQuery
    with patch.object(CallbackQuery, 'answer', new_callable=AsyncMock) as mock_answer:
        
        expected_answer = i18n.desk.booker.success(date=first_date_button, room_name=first_room_button, desk_name=first_desk_button)
        
        mock_answer.return_value = expected_answer # Set return value for the mock
        
        message_manager.reset_history()
        
        logger.info(f"Clicking on the first desk button: {first_desk_button}")
        
        desk_button_callback_id: str = await click_inline_keyboard_button_by_location(
            test_user=test_user,
            message=desk_selection_message,
            row=0,
            column=0,
        )
        
        message_manager.assert_answered(callback_id=desk_button_callback_id)
        logger.debug(f"Callback message has been answered. Callback ID: {desk_button_callback_id}")
        
        mock_answer.assert_called_once_with(text=expected_answer, show_alert=True)

        actual_answer = mock_answer.call_args[1]['text']  # Retrieve the actual answer passed to the answer method
        show_alert = mock_answer.call_args[1]['show_alert']  # Retrieve the 'show_alert' flag passed to the answer method
        
        assert_callback_answer(
            callback_answer=actual_answer,
            expected_answer=expected_answer,
            show_alert=show_alert,
        )

    #* CHECKING DATABASE RECORD

    logger.debug("Checking the database for a booking record.")
    booking_date: datetime = datetime.strptime(first_date_button, str(config.bot_operation.date_format))
    try:
        booking: Booking | None = await orm_select_booking_by_telegram_id_and_date_selectinload(
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
    
    pass


async def booking_dialog_random_desk(
    test_users: List[User],
    i18n: TranslatorRunner,
    dp: Dispatcher,
    message_manager: MockMessageManager,
    config: Config,
):
    logger.debug("Setting up test users:")
    logger.debug(f"Test users: {test_users}")
    # Iterating through the test users starting from the second user and create a BotClient for each user, where user_id=telegram_id, chat_id=telegram_id
    for user in test_users[1:]:
        logger.debug(f"User: {user.telegram_name} with ID: {user.telegram_id} is being set up.")
        telegram_id = user.telegram_id
        telegram_name = user.telegram_name
        test_user = BotClient(
            dp,
            user_id=telegram_id,
            chat_id=telegram_id)
        
        message_manager.reset_history()
        
        logger.info(f"User: {telegram_name} is sending '/book' command.")
        await test_user.send(text="/book")
        
        date_selection_message = message_manager.one_message()
        
        # Get location of date button with random row an column=0
        row: int = random.randint(0, int(config.bot_operation.num_days) - 1) # type: ignore
        column: int = 0
        
        message_manager.reset_history()
        
        logger.info(f"Clicking on date button located at random row and column=0 ({row},{column}).")
        rndm_date_btn_callback_id = await click_inline_keyboard_button_by_location(
            test_user=test_user,
            message=date_selection_message,
            row=row,
            column=column,
        )
        
        message_manager.assert_answered(callback_id=rndm_date_btn_callback_id)
        logger.debug(f"Callback message has been answered. Callback ID: {rndm_date_btn_callback_id}")
        
        room_selection_message = message_manager.one_message()
        rndm_desk_btn = i18n.booking.random.button()

        # Mocking the answer method in CallbackQuery
        with patch.object(CallbackQuery, 'answer', new_callable=AsyncMock) as mock_answer:
            
            message_manager.reset_history()
            
            logger.info("Clicking on random desk button.")
            rndm_desk_btn_callback_id = await click_inline_keyboard_button_by_text(
                test_user=test_user,
                message=room_selection_message,
                button_text=rndm_desk_btn,
            )
        
            message_manager.assert_answered(callback_id=rndm_desk_btn_callback_id)
            logger.debug(f"Callback message has been answered. Callback ID: {rndm_desk_btn_callback_id}")
            
            mock_answer.assert_called_once()
            show_alert = mock_answer.call_args[1]['show_alert']
            assert show_alert is True
            
            # TODO: Add check for actual answer text. Required logic before that to get expected answer after clicking random desk button.
            logger.info(
                f"Callback answer:\n\n"
                f"{mock_answer.call_args[1]['text']}\n"
            )
            
            assert_callback_answer(
                callback_answer=None,
                expected_answer=None,
                show_alert=show_alert,
            )
            
    pass


async def all_bookings_dialog(
    test_users: List[User],
    i18n: TranslatorRunner,
    dp: Dispatcher,
    message_manager: MockMessageManager,
    config: Config,
    session: AsyncSession,
):
    logger.info(f"Setting up test user with ID: {test_users[0].telegram_id} and name: {test_users[0].telegram_name}.")
    telegram_id: int = test_users[0].telegram_id
    test_user = BotClient(
        dp,
        user_id=telegram_id,
        chat_id=telegram_id)
    
    message_manager.reset_history()
    
    logger.info("Sending '/all_bookings' command.")
    await test_user.send(text="/all_bookings")
    
    #* ROOM SELECTION 1
    
    logger.debug("Getting rooms.")
    rooms: List[Tuple[int, str]] = await generate_available_rooms_as_list_of_tuples(session)
    
    # Transform list of tuples into list of room names(str)
    room_names: List[str] = [room[1] for room in rooms]
    
    room_selection_message = message_manager.one_message()
    
    assert_message_text(
        message=room_selection_message,
        expected_text=i18n.select.room(),
    )
    
    log_inline_keyboard_buttons(room_selection_message)
    
    logger.debug("Matching expected rooms with buttons on UI.")
    assert_inline_keyboard_buttons(
        expected_texts=room_names,
        message=room_selection_message,
    )

    first_room_id = rooms[0][0]
    first_room_button = room_selection_message.reply_markup.inline_keyboard[0][0].text # type: ignore
    
    message_manager.reset_history()
    
    logger.info(f"Clicking on the first room button: {first_room_button}")
    room_button_callback_id = await click_inline_keyboard_button_by_location(
        test_user=test_user,
        message=room_selection_message,
        row=0,
        column=0,
    )
    
    message_manager.assert_answered(callback_id=room_button_callback_id)
    logger.debug(f"Callback message has been answered. Callback ID: {room_button_callback_id}")
    
    #* BOOKINGS LIST 1
    
    logger.debug("Getting bookings list.")
    bookings = await generate_current_bookings_list_by_room_id(
        i18n,
        session,
        date_format=str(config.bot_operation.date_format),
        date_format_short=str(config.bot_operation.date_format_short),
        room_id=first_room_id,
    )
    
    bookings_list_message = message_manager.one_message()
    
    assert_message_text(
        message=bookings_list_message,
        expected_text=bookings[1],
    )
    
    #* BACK BUTTON
    
    log_inline_keyboard_buttons(bookings_list_message)
    
    assert_inline_keyboard_buttons(
        expected_texts=i18n.button.back(),
        message=bookings_list_message,
    )
    
    message_manager.reset_history()
    
    logger.info("Clicking on Back button.")
    exit_button_callback_id = await click_inline_keyboard_button_by_text(
        test_user=test_user,
        message=bookings_list_message,
        button_text=i18n.button.back(),
    )
    
    #* ROOM SELECTION 2
    
    room_selection_2_message = message_manager.one_message()
    
    second_room_id = rooms[1][0]
    second_room_button = room_selection_2_message.reply_markup.inline_keyboard[1][0].text # type: ignore
    
    message_manager.reset_history()
    
    logger.info(f"Clicking on the second room button: {second_room_button}")
    room_button_callback_id = await click_inline_keyboard_button_by_location(
        test_user=test_user,
        message=room_selection_message,
        row=1,
        column=0,
    )
    
    message_manager.assert_answered(callback_id=room_button_callback_id)
    logger.debug(f"Callback message has been answered. Callback ID: {room_button_callback_id}")
    
    #* BOOKINGS LIST 2
    
    logger.debug("Getting bookings list.")
    bookings_2 = await generate_current_bookings_list_by_room_id(
        i18n,
        session,
        date_format=str(config.bot_operation.date_format),
        date_format_short=str(config.bot_operation.date_format_short),
        room_id=second_room_id,
    )
    
    bookings_list_message_2 = message_manager.one_message()
    
    assert_message_text(
        message=bookings_list_message_2,
        expected_text=bookings_2[1],
    )
    
    #* EXIT BUTTON
    
    log_inline_keyboard_buttons(bookings_list_message)
    
    assert_inline_keyboard_buttons(
        expected_texts=i18n.button.exit(),
        message=bookings_list_message,
    )
    
    message_manager.reset_history()
    
    logger.info("Clicking on Exit button.")
    exit_button_callback_id = await click_inline_keyboard_button_by_text(
        test_user=test_user,
        message=bookings_list_message,
        button_text=i18n.button.exit(),
    )
    
    message_manager.assert_answered(callback_id=exit_button_callback_id)
    logger.debug(f"Callback message has been answered. Callback ID: {exit_button_callback_id}")
    
    pass


async def cancel_bookings_dialog(
    test_users: List[User],
    i18n: TranslatorRunner,
    dp: Dispatcher,
    message_manager: MockMessageManager,
    config: Config,
    session: AsyncSession,
):
    logger.info(f"Setting up test user with ID: {test_users[0].telegram_id} and name: {test_users[0].telegram_name}.")
    telegram_id: int = test_users[0].telegram_id
    test_user = BotClient(
        dp,
        user_id=telegram_id,
        chat_id=telegram_id)
    
    message_manager.reset_history()
    
    logger.info("Sending '/cancel' command.")
    await test_user.send(text="/cancel")
    
    if not message_manager.sent_messages:
        logger.error(f"No messages were captured, expected at least one. Messages: {message_manager.sent_messages}.")
        assert False, "Expected at least one message but got none."
    
    if len(message_manager.sent_messages) > 1:
        log_sent_messages(message_manager)
        assert False, "Expected one message but multiple were captured."
    
    if len(message_manager.sent_messages) == 1:
        booking_selection_message = message_manager.sent_messages[0]
        expected_message = i18n.select.booking.to.cancel()
        assert_message_text(booking_selection_message, expected_message)
    
    logger.debug("Getting bookings list.")
    bookings: Union[List[Tuple[int, str]], str] = await generate_current_bookings_by_telegram_id(
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
        # Transform the list of tuples into a list of bookings data(str)
        bookings_list: List[str] = [booking[1] for booking in bookings]
    
    log_inline_keyboard_buttons(booking_selection_message)
    
    logger.debug("Matching expected bookings with buttons on UI.")
    assert_inline_keyboard_buttons(
        expected_texts=bookings_list,
        message=booking_selection_message,
    )
    
    first_booking_id = bookings[0][0]
    first_booking_button = booking_selection_message.reply_markup.inline_keyboard[0][0].text # type: ignore
    
    # Mocking the answer method in CallbackQuery
    with patch.object(CallbackQuery, 'answer', new_callable=AsyncMock) as mock_answer:
        
        expected_answer = i18n.cancel.booking.success()
        
        mock_answer.return_value = expected_answer
        
        message_manager.reset_history()
        
        logger.info(f"Clicking on the first booking button: {first_booking_button}")
        
        booking_button_callback_id = await click_inline_keyboard_button_by_location(
            test_user=test_user,
            message=booking_selection_message,
            row=0,
            column=0,
        )
            
        message_manager.assert_answered(callback_id=booking_button_callback_id)
        logger.debug(f"Callback message has been answered. Callback ID: {booking_button_callback_id}")
        
        mock_answer.assert_called_once_with(text=expected_answer)
        
        actual_answer = mock_answer.call_args[1]['text']
        
        assert_callback_answer(
            callback_answer=actual_answer,
            expected_answer=expected_answer,
            show_alert=None,
        )
        
    #* CHECKING DATABASE RECORD

    logger.debug("Checking the database for a booking record.")
    try:
        booking_obj: Booking | None = await orm_select_booking_by_id(
        session,
        booking_id=first_booking_id,
        )
    except Exception as e:
        logger.error(f"Failed to retrieve booking record: {e}")
        raise
    
    if booking_obj is None:
        logger.debug("Booking record not found in the database.")
    
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

    #* TRUNCATE DATABASE TABLES
    
    logger.debug("Truncating database tables.")
    await truncate_db_cascade(session)
    
    pass