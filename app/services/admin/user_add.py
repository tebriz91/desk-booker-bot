import re
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import (
    orm_select_user_by_telegram_id_or_telegram_name,
    orm_insert_user,
    orm_select_user_from_waitlist_by_telegram_name)

class UserInputError(Exception):
    pass

class InputError(Exception):
    pass

# User add service with string parsing and input validation
async def user_add_service_with_string_parsing(session: AsyncSession, user_input: str) -> str:
    if not user_input or " " not in user_input:
        raise UserInputError("Please enter a valid input in the format: ID @username\nFor example: 123456789 @username")

    # Retrieve the user's input
    try:
        telegram_id_str, telegram_name_raw = user_input.split(maxsplit=1)
        telegram_id = int(telegram_id_str)
        
        # Validate telegram_id length
        if len(telegram_id_str) < 5 or len(telegram_id_str) > 12:
            raise UserInputError("The Telegram ID must be longer than 5 digits but less than 13 digits.")
        
        telegram_name = telegram_name_raw.strip("@")  # Remove '@' if present
    except ValueError:
        raise UserInputError("The Telegram ID should be a number. Please try again.")

    # Validate telegram_name according to Telegram API documentation https://core.telegram.org/method/account.checkUsername
    if not re.match(r'^[A-Za-z0-9_]{5,32}$', telegram_name):
        raise UserInputError("Username must be 5-32 characters long, can include letters (A-z, case-insensitive), numbers (0-9), and underscores. Please try again.")

    # Check if the user already exists
    existing_user = await orm_select_user_by_telegram_id_or_telegram_name(session, telegram_id, telegram_name)
    if existing_user:
        raise UserInputError("User already exists.")

    await orm_insert_user(session, telegram_id, telegram_name)
    return f"User @{telegram_name} has been added"

# User add service by telegram_name from the waitlist table
async def user_add_service_by_telegram_name_from_wl(session: AsyncSession, telegram_name: str) -> str:
    # Validate telegram_name
    if not re.match(r'^[A-Za-z0-9_]{5,32}$', telegram_name):
        raise InputError("Username must be 5-32 characters long, can include letters (A-z, case-insensitive), numbers (0-9), and underscores.")
    
    # Retrieve telegram_id, first_name, last_name from the waitlist table
    waitlist_user_obj = await orm_select_user_from_waitlist_by_telegram_name(session, telegram_name)
    telegram_id = waitlist_user_obj.telegram_id
    first_name = waitlist_user_obj.first_name
    last_name = waitlist_user_obj.last_name
    
    # Check if the user already exists
    existing_user = await orm_select_user_by_telegram_id_or_telegram_name(session, telegram_id, telegram_name)
    if existing_user:
        raise InputError("User already exists.")

    await orm_insert_user(
        session,
        telegram_id,
        telegram_name,
        first_name,
        last_name)
    return f"User @{telegram_name} has been added"