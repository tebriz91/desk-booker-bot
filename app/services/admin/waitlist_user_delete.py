from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_delete_user_from_waitlist_by_telegram_name

class InputError(Exception):
    pass

async def waitlist_user_delete_by_username_service(session: AsyncSession, telegram_name: str) -> str:

    # Validate input is not empty
    if not telegram_name:
        raise InputError("InputError: Telegram name missing.")
    
    try:
        await orm_delete_user_from_waitlist_by_telegram_name(session, telegram_name)
        return f"User @{telegram_name} has been deleted from the waitlist."
    except Exception as e:
        raise InputError(f"Error: {e}")