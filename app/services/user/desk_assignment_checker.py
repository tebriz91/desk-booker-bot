from typing import TYPE_CHECKING, Tuple
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.orm_queries import (
    orm_select_desk_assignment_by_telegram_id_and_weekday,
    orm_select_desk_assignments_by_telegram_id_selectinload,
    orm_select_is_out_of_office_by_telegram_id,
)

from app.database.enums.weekdays import Weekday

if TYPE_CHECKING:
    from app.locales.stub import TranslatorRunner # type: ignore


async def check_desk_assignment(i18n, session: AsyncSession, telegram_id: int, date: str, date_format: str) -> bool | str:
    i18n: TranslatorRunner = i18n
    # Parse date string to datetime.date type: 'YYYY-MM-DD' to query the database. And handle incorrect date format.
    try:
        booking_date = datetime.strptime(date, date_format).date()
    except ValueError as e:
        return "Error: Incorrect date format. Parsing date to datetime.date failed."
    # Convert integer weekday to Weekday enum
    weekday = Weekday(booking_date.weekday())
    # Check if the user has assigned desk for the weekday of the selected date
    try:
        # To avoid lazy loading, use selectinload to load the related objects (room and desk) in one query.
        desk_assignment = await orm_select_desk_assignment_by_telegram_id_and_weekday(session, telegram_id, weekday)
        if not desk_assignment:
            return False
        else:
            #! desk-assignment
            return i18n.desk.assignment(weekday=booking_date.strftime('%A'))
    except Exception as e:
        return f"An unexpected error {e} occurred while checking for desk assignments."
    

async def check_desk_assignment_by_telegram_id(
    i18n,
    session: AsyncSession,
    telegram_id: int,
    ) -> Tuple[str, str]:
    '''
    Returns a tuple of two strings: the first string a tag for the response, and the second string is the response message.
    '''
    i18n: TranslatorRunner = i18n
    assignments = await orm_select_desk_assignments_by_telegram_id_selectinload(session, telegram_id)
    if not assignments:
        #! desk-assignment-empty
        return ("empty", i18n.desk.assignment.empty())
    else:
        #! desk-assignment-greeting
        result: str = i18n.desk.assignment.greeting() + '\n\n'
        for assignment in assignments:
            #! desk-assignment-info
            result += i18n.desk.assignment.info(
                weekday=assignment.weekday.name,
                room_name=assignment.desk.room.name,
                desk_name=assignment.desk.name,
            ) + '\n\n'
    try:
        is_out_of_office: bool = await orm_select_is_out_of_office_by_telegram_id(session, telegram_id)
        if is_out_of_office:
            #! desk-assignment-inactive
            result += i18n.desk.assignment.inactive()
            return ("inactive", result)
        else:
            #! desk-assignment-active
            result += i18n.desk.assignment.active()
            return ("active", result)
    except Exception as e:
        return ("error", str(e))