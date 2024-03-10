import re
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_select_user_by_telegram_id_or_telegram_name, orm_insert_user

class UserInputError(Exception):
    pass

async def user_add_service(session: AsyncSession, user_input: str) -> str:
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
    return "User has been added"