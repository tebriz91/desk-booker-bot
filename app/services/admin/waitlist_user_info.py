from sqlalchemy.ext.asyncio import AsyncSession

from app.database.orm_queries import orm_select_user_from_waitlist_by_telegram_name


async def waitlist_user_info_service(session: AsyncSession, telegram_name: str) -> str:
    try:
        # Retrieve user info from waitlist by telegram_name
        user = await orm_select_user_from_waitlist_by_telegram_name(session, telegram_name)
        
        # Format user info
        user_info = (
            f"Press 'Yes' to add user, 'No' to remove user from the waitlist \n\n"
            f"<b>Telegram ID</b>: {user.telegram_id}\n"
            f"<b>Telegram name</b>: @{user.telegram_name}\n"
            f"<b>First name</b>: {user.first_name}\n"
            f"<b>Last name</b>: {user.last_name}\n"
            f"<b>Applied at</b>: {user.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        )
        return user_info
    
    except Exception as e:
        user_info = f"Error: {e}"
        return user_info