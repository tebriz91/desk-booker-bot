import re
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.orm_queries import orm_select_user_by_telegram_name, orm_delete_user_by_telegram_name


class UserInputError(Exception):
    pass


async def user_delete_by_username_service(session: AsyncSession, user_input: str) -> str:
    # Validate input is not empty
    if not user_input:
        raise UserInputError("Please enter a valid Telegram username.")

    # Format the username to remove '@' if present
    username = user_input.removeprefix('@')

    # Validate username format
    if not re.match(r'^[A-Za-z0-9_]{5,32}$', username):
        raise UserInputError("Username must be 5-32 characters long, can include letters (A-z, case-insensitive), numbers (0-9), and underscores. Please try again.")

    # Check if the user exists
    existing_user = await orm_select_user_by_telegram_name(session, username)
    if not existing_user:
        raise UserInputError("User does not exist.")

    # Perform the deletion
    await orm_delete_user_by_telegram_name(session, username)
    return "User has been deleted successfully."