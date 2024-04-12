from typing import TYPE_CHECKING, Tuple
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import (
    orm_select_desk_assignment_by_telegram_id_and_weekday,
    orm_select_desk_assignments_by_telegram_id_selectinload,
    orm_select_is_out_of_office_by_telegram_id,
)

from database.enums.weekdays import Weekday

if TYPE_CHECKING:
    from locales.stub import TranslatorRunner

from utils.logger import Logger

logger = Logger()


async def check_desk_assignment(i18n, session: AsyncSession, telegram_id: int, date: str, date_format: str) -> bool | str:
    i18n: TranslatorRunner = i18n
    # Parse date string to datetime.date type: 'YYYY-MM-DD' to query the database. And handle incorrect date format.
    try:
        booking_date = datetime.strptime(date, date_format).date()
    except ValueError as e:
        return "Error: Incorrect date format. Parsing date to datetime.date failed."
    # Convert integer weekday to Weekday enum
    weekday = Weekday(booking_date.weekday())
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Weekday: {weekday}")
    # Check if the user has assigned desk for the weekday of the selected date
    try:
        # To avoid lazy loading, use selectinload to load the related objects (room and desk) in one query.
        desk_assignment = await orm_select_desk_assignment_by_telegram_id_and_weekday(session, telegram_id, weekday)
        logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Desk assignment: {desk_assignment}")
        if not desk_assignment:
            return False
        else:
            #! desk-assignment
            return i18n.desk.assignment(weekday=booking_date.strftime('%A'))
    except Exception as e:
        return "An unexpected error occurred while checking for desk assignments."
    

async def check_desk_assignment_by_telegram_id(
    i18n,
    session: AsyncSession,
    telegram_id: int,
    ) -> Tuple[str, str]:
    '''
    Returns a tuple of two strings: the first string a tag for the response, and the second string is the response message.
    '''
    i18n: TranslatorRunner = i18n
    desk_assignment = await orm_select_desk_assignments_by_telegram_id_selectinload(session, telegram_id)
    if not desk_assignment:
        #! desk-assignment-empty
        return ("empty", i18n.desk.assignment.empty())
    else:
        # Iterate over the desk assignments to get the string of ordered weekdays
        weekdays = ', '.join([assignment.weekday.name for assignment in desk_assignment])
        #! desk-assignment-exists
        result: str = i18n.desk.assignment.exists(
            desk_name=desk_assignment[0].desk.name,
            room_name=desk_assignment[0].desk.room.name,
            weekdays=weekdays,
        )
    try:
        is_out_of_office: bool = await orm_select_is_out_of_office_by_telegram_id(session, telegram_id)
        if is_out_of_office:
            #! desk-assignment-inactive
            result += '\n\n' + i18n.desk.assignment.inactive()
            return ("inactive", result)
        else:
            #! desk-assignment-active
            result += '\n\n' + i18n.desk.assignment.active()
            return ("active", result)
    except Exception as e:
        return ("error", str(e))