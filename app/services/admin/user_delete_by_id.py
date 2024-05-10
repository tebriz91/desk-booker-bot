from sqlalchemy.ext.asyncio import AsyncSession

from app.database.orm_queries import orm_select_user_by_telegram_id, orm_delete_user_by_telegram_id


class UserInputError(Exception):
    pass


async def user_delete_by_id_service(session: AsyncSession, user_input: str) -> str:
    # Validate user_input is not empty and is numeric
    if not user_input or not user_input.isdigit():
        raise UserInputError("Please enter a valid Telegram ID containing only numbers without spaces.")
        
    # Convert user_input to an integer
    try:
        telegram_id = int(user_input)
    except ValueError:
        # This block is technically redundant due to the isdigit() check but included for completeness
        raise UserInputError("The Telegram ID should be a numeric value. Please try again.")
        
    # Validate telegram_id length; adjust according to Telegram's specifications
    if len(user_input) < 5 or len(user_input) > 12:
        raise UserInputError("The Telegram ID must be longer than 4 digits and less than 13 digits.")
        
    # Check if the user exists
    existing_user = await orm_select_user_by_telegram_id(session, telegram_id)
    if not existing_user:
        raise UserInputError("User does not exist.")
    
    # Delete the user by their Telegram ID
    await orm_delete_user_by_telegram_id(session, telegram_id)
    return "User has been deleted."