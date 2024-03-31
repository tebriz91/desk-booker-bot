from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_select_desk_assignment_by_telegram_id_and_weekday

from utils.logger import Logger

logger = Logger()

async def check_desk_assignment(session: AsyncSession, telegram_id: int, date: str, date_format: str) -> bool | str:
    # Parse date string to datetime.date type: 'YYYY-MM-DD' to query the database. And handle incorrect date format.
    try:
        booking_date = datetime.strptime(date, date_format).date()
    except ValueError as e:
        return f"Error: Incorrect date format. Parsing date to datetime.date failed."
    
    weekday = booking_date.weekday()
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Weekday: {weekday}")
    # Check if the user has assigned desk for the weekday of the selected date
    try:
        # To avoid lazy loading, use selectinload to load the related objects (room and desk) in one query.
        desk_assignment = await orm_select_desk_assignment_by_telegram_id_and_weekday(session, telegram_id, weekday)
        logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Desk assignment: {desk_assignment}")
        if not desk_assignment:
            return False
        else:
            return f"You already have an assigned desk for the selected weekday."
    except Exception as e:
        return "An unexpected error occurred while checking for desk assignments."