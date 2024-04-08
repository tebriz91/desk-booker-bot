from datetime import date

from sqlalchemy import Integer, and_, func, literal, not_, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload, aliased
from sqlalchemy.exc import SQLAlchemyError

from database.models import (
    User,
    UserRoleAssignment,
    Team,
    TeamTree,
    Waitlist,
    Room,
    Desk,
    DeskAssignment,
    Booking,
)

from database.enums.weekdays import Weekday

from utils.logger import Logger


logger = Logger()


class DeskBookerError(Exception):
    pass


#* User's ORM queries
async def orm_insert_user(
    session: AsyncSession,
    telegram_id: int,
    telegram_name: str,
    first_name: str | None = None,
    last_name: str | None = None):
    # Check if the user is already in the database
    query = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(query)
    user = result.first()
    # Add a new user only if they do not already exist
    if user is None:
        new_user = User(
            telegram_id=telegram_id,
            telegram_name=telegram_name,
            first_name=first_name,
            last_name=last_name)
        session.add(new_user)
        await session.commit()
    else:
        raise Exception


async def orm_select_users(session: AsyncSession):
    query = select(User)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_select_user_by_telegram_id(session: AsyncSession, telegram_id: int):
    query = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_select_user_by_telegram_name(session: AsyncSession, telegram_name: str):
    query = select(User).where(User.telegram_name == telegram_name)
    result = await session.execute(query)
    return result.scalar()


async def orm_select_user_by_telegram_id_or_telegram_name(
    session: AsyncSession,
    telegram_id: int,
    telegram_name: str):
    query = select(User).where(
        (User.telegram_id == telegram_id) | (User.telegram_name == telegram_name)
    )
    result = await session.execute(query)
    return result.scalar()


async def orm_delete_user_by_telegram_id(session: AsyncSession, telegram_id: int):
    query = delete(User).where(User.telegram_id == telegram_id)
    await session.execute(query)
    await session.commit()


async def orm_delete_user_by_telegram_name(session: AsyncSession, telegram_name: str):
    query = delete(User).where(User.telegram_name == telegram_name)
    await session.execute(query)
    await session.commit()


#* UserRoleAssignment's ORM queries
async def get_user_teams_and_roles(session, telegram_id):
    query = select(
        UserRoleAssignment.team_id,
        Team.name.label('team_name'),
        UserRoleAssignment.role
    ).join(
        Team, UserRoleAssignment.team_id == Team.id
    ).where(
        UserRoleAssignment.telegram_id == telegram_id
    )
    
    result = await session.execute(query)
    return result.fetchall()


#* Team's ORM queries
# async def orm_select_user_team_id(session: AsyncSession, telegram_id: int):
#     query = select(User.team_id).where(User.telegram_id == telegram_id)
#     result = await session.execute(query)
#     return result.scalar_one()


async def orm_select_team_id_by_telegram_id(session: AsyncSession, telegram_id: int):
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Inside orm_select_team_id_by_telegram_id()")
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Telegram ID: {telegram_id}")
    query = select(UserRoleAssignment.team_id).where(UserRoleAssignment.telegram_id == telegram_id)
    result = await session.execute(query)
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Result of ORM query: {result}")
    return result.scalar_one()


async def orm_select_team_preferred_room_id(session: AsyncSession, team_id: int):
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Inside orm_select_team_preferred_room_id()")
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Team ID: {team_id}")
    query = select(Team.room_id).where(Team.id == team_id)
    result = await session.execute(query)
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Result of ORM query: {result}")
    return result.scalar_one()


#* TeamTree's ORM queries
async def orm_select_team_tree(session: AsyncSession, parent_team_id: int):
    # Define a recursive CTE to fetch the team hierarchy
    c = select(
        TeamTree.child_team_id.label('team_id'),
        func.cast(literal('1'), Integer).label('depth')  # Starting depth
    ).where(TeamTree.parent_team_id == parent_team_id).cte(name="team_hierarchy", recursive=True)

    recursive_query = select(
        TeamTree.child_team_id,
        (c.c.depth + 1).label('depth')
    ).join_from(TeamTree, c, TeamTree.parent_team_id == c.c.team_id)

    c = c.union_all(recursive_query)

    # Final query using the CTE to fetch team details
    final_query = select(
        Team.name,
        c.c.depth
    ).select_from(Team.join(c, Team.id == c.c.team_id))

    # Execution with await
    results = await session.execute(final_query)
    teams = results.fetchall()

    return teams


#* Waitlist's ORM queries
async def orm_insert_user_to_waitlist(
    session: AsyncSession,
    telegram_id: int,
    telegram_name: str,
    first_name: str | None = None,
    last_name: str | None = None):
    query = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(query)
    user = result.first()
    if user is None:
        new_user = Waitlist(
            telegram_id=telegram_id,
            telegram_name=telegram_name,
            first_name=first_name,
            last_name=last_name)
        session.add(new_user)
        await session.commit()
    else:
        raise Exception


async def orm_select_user_from_waitlist_by_telegram_id(session: AsyncSession, telegram_id: int):
    query = select(Waitlist).where(Waitlist.telegram_id == telegram_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_select_user_from_waitlist_by_telegram_name(session: AsyncSession, telegram_name: str):
    query = select(Waitlist).where(Waitlist.telegram_name == telegram_name)
    result = await session.execute(query)
    return result.scalar()


async def orm_select_telegram_id_from_waitlist_by_telegram_name(session: AsyncSession, telegram_name: str):
    query = select(Waitlist.telegram_id).where(Waitlist.telegram_name == telegram_name)
    result = await session.execute(query)
    return result.scalar_one()


async def orm_select_users_from_waitlist(session: AsyncSession):
    query = select(Waitlist)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_user_from_waitlist_by_telegram_id(session: AsyncSession, telegram_id: int):
    query = delete(Waitlist).where(Waitlist.telegram_id == telegram_id)
    await session.execute(query)
    await session.commit()


async def orm_delete_user_from_waitlist_by_telegram_name(session: AsyncSession, telegram_name: str):
    query = delete(Waitlist).where(Waitlist.telegram_name == telegram_name)
    await session.execute(query)
    await session.commit()


#* Room's ORM queries
async def orm_insert_room(session: AsyncSession, room_name: str):
    query = select(Room).where(Room.name == room_name)
    result = await session.execute(query)
    room = result.first()
    if room is None:
        new_room = Room(name=room_name)
        session.add(new_room)
        await session.commit()
    else:
        raise Exception


async def orm_select_rooms(session: AsyncSession):
    query = select(Room)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_select_available_rooms(session: AsyncSession):
    query = select(Room).where(Room.is_available == True)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_select_room_id_by_name(session: AsyncSession, room_name: str):
    query = select(Room.id).where(Room.name == room_name)
    result = await session.execute(query)
    return result.scalar_one()


async def orm_select_room_by_name(session: AsyncSession, room_name: str):
    query = select(Room).where(Room.name == room_name)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_room_name_by_name(session: AsyncSession, old_room_name: str, new_room_name: str):
    query = update(Room).where(Room.name == old_room_name).values(name=new_room_name)
    await session.execute(query)
    await session.commit()


async def orm_delete_room_by_name(session: AsyncSession, room_name: str):
    query = delete(Room).where(Room.name == room_name)
    await session.execute(query)
    await session.commit()


async def orm_get_room_availability_by_name(session: AsyncSession, room_name: str):
    query = select(Room.is_available).where(Room.name == room_name)
    result = await session.execute(query)
    return result.scalar_one()


async def orm_update_room_availability_by_name(session: AsyncSession, room_name: str, is_available: bool):
    query = update(Room).where(Room.name == room_name).values(is_available=is_available)
    await session.execute(query)
    await session.commit()


async def orm_get_room_data_by_name(session: AsyncSession, room_name: str):
    query = select(Room).where(Room.name == room_name)
    result = await session.execute(query)
    return result.scalar()


async def orm_select_room_plan_by_room_name(session: AsyncSession, room_name: str):
    query = select(Room.plan).where(Room.name == room_name)
    result = await session.execute(query)
    return result.scalar_one()


#* Desk's ORM queries
async def orm_insert_desk_with_room_id(session: AsyncSession, room_id: int, desk_name: str):
    query = select(Desk).where(Desk.name == desk_name)
    result = await session.execute(query)
    desk = result.first()
    if desk is None:
        new_desk = Desk(room_id=room_id, name=desk_name)
        session.add(new_desk)
        await session.commit()
    else:
        raise Exception


async def orm_select_desk_id_by_name(session: AsyncSession, desk_name: str):
    query = select(Desk.id).where(Desk.name == desk_name)
    result = await session.execute(query)
    return result.scalar_one()


async def orm_select_desk_by_name(session: AsyncSession, desk_name: str):
    query = select(Desk).where(Desk.name == desk_name)
    result = await session.execute(query)
    return result.scalar()


async def orm_select_desks_by_room_id(session: AsyncSession, room_id: int):
    query = select(Desk).where(Desk.room_id == room_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_select_available_desks_by_room_id(session: AsyncSession, room_id: int):
    query = select(Desk).where(Desk.room_id == room_id, Desk.is_available == True)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_select_desks_by_room_name(session: AsyncSession, room_name: str):
    query = select(Desk).join(Room).where(Room.name == room_name)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_select_available_desks_by_room_name(session: AsyncSession, room_name: str):
    query = select(Desk).join(Room).where(Room.name == room_name, Desk.is_available == True)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_select_available_not_booked_desks_by_room_id(session: AsyncSession, room_id: int, date: date):
    # Create an alias for bookings to use in the subquery
    booking_alias = aliased(Booking)
    # Subquery to check if a desk is booked on the given date
    desk_booked_subquery = (
        select(1)
        .where(
            and_(
                booking_alias.desk_id == Desk.id,  # Ensure the subquery is correlated with the main query's desk
                booking_alias.date == date,
            )
        )
        .exists()
    )
    # Main query to find desks that are available and not booked on the specified date
    query = (
        select(Desk)
        .where(
            and_(
                Desk.room_id == room_id,
                Desk.is_available == True,
                not_(desk_booked_subquery)  # Use `not_` to exclude desks that fulfill the subquery condition
            )
        )
    )
    result = await session.execute(query)
    return result.scalars().all()


async def orm_select_not_assigned_desks_by_desks_id_and_weekday(session: AsyncSession, desk_ids: list[int], weekday: Weekday):
    logger.info(">>>>>>>>>>>>>>>>>>>>>>>Inside orm_select_not_assigned_desks_by_desks_id_and_weekday()")
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Weekday: {weekday}")
    subquery = select(DeskAssignment.desk_id).where(
        DeskAssignment.weekday == weekday,
        DeskAssignment.desk_id.in_(desk_ids)
    ).distinct()
    # Use the subquery to filter out desks that have been assigned on this weekday
    query = select(Desk).where(
        Desk.id.in_(desk_ids),
        ~Desk.id.in_(subquery)
    )
    result = await session.execute(query)
    return result.scalars().all()


async def orm_select_available_not_assigned_desks_by_room_id(session: AsyncSession, room_id: int, weekday: int):
    logger.info(">>>>>>>>>>>>>>>>>>>>>>>Inside orm_select_available_not_assigned_desks_by_room_id()")
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Room ID: {room_id}")
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Weekday: {weekday}")
    
    # Subquery to find desk ids that have been assigned on the given weekday
    assigned_desk_ids_subquery = (
        select(DeskAssignment.desk_id)
        .where(DeskAssignment.weekday == weekday)
        .distinct()
    ).subquery()

    # Main query to select desks from the specified room that are available and not in the list of assigned desks
    query = (
        select(Desk.name)
        .join(Room, Room.id == Desk.room_id)
        .where(Room.id == room_id, Desk.is_available == True, Desk.id.notin_(assigned_desk_ids_subquery))
    )
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Main query: {query}")

    result = await session.execute(query)
    desks = result.scalars().all()

    if desks:
        logger.info(f"Available desks: {desks}")
    else:
        logger.info("No available desks found.")

    return desks


async def orm_select_available_not_booked_desks_by_room_name(session: AsyncSession, room_name: str, date: date):
    # This subquery checks for desks that have a booking on the specified date
    booking_subquery = (
        select(Booking.desk_id)
        .where(Booking.date == date)
        .correlate(Desk)
        .exists()
    )
    # Main query selects desks that are available, in the specified room,
    # and not in the subquery (i.e., not booked on the specified date)
    query = (
        select(Desk)
        .join(Room)
        .where(
            and_(
                Room.name == room_name,
                Desk.is_available == True,
                not_(booking_subquery)  # Not booked on the specified date
            )
        )
    )
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_desk_availability_by_name(session: AsyncSession, desk_name: str):
    query = select(Desk.is_available).where(Desk.name == desk_name)
    result = await session.execute(query)
    return result.scalar_one()


async def orm_update_desk_name_by_id(session: AsyncSession, desk_id: int, new_desk_name: str):
    query = update(Desk).where(Desk.id == desk_id).values(name=new_desk_name)
    await session.execute(query)
    await session.commit()


async def orm_update_desk_name_by_name(session: AsyncSession, desk_name: str, new_desk_name: str):
    query = update(Desk).where(Desk.name == desk_name).values(name=new_desk_name)
    await session.execute(query)
    await session.commit()


async def orm_update_desk_availability_by_name(session: AsyncSession, desk_name: str, is_available: bool):
    query = update(Desk).where(Desk.name == desk_name).values(is_available=is_available)
    await session.execute(query)
    await session.commit()


async def orm_delete_desk_by_id(session: AsyncSession, desk_id: int):
    query = delete(Desk).where(Desk.id == desk_id)
    await session.execute(query)
    await session.commit()


#* DeskAssignment's ORM queries
async def orm_insert_desk_assignment():
    pass


async def orm_select_desk_assignment_by_telegram_id_and_weekday(session: AsyncSession, telegram_id: int, weekday: Weekday):
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Telegram ID: {telegram_id}")
    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Weekday: {weekday}")
    
    # Directly query DeskAssignment by telegram_id and weekday, joining with User to access telegram_id
    query = select(DeskAssignment).join(User).where(
        User.telegram_id == telegram_id,
        DeskAssignment.weekday == weekday
    )
    result = await session.execute(query)
    desk_assignment = result.scalars().first()  # Using first() as we're now handling potentially multiple matches in one step
    
    if desk_assignment:
        logger.info(f">>>>>>>>>>>>>>>>>>>>>>>Desk assignment ID: {desk_assignment.id}")
        return desk_assignment
    else:
        logger.info("No desk assignment found for the given Telegram ID and weekday.")
        return None


async def orm_select_desk_assignments_by_user_id(session: AsyncSession, user_id: int):
    query = select(DeskAssignment).where(DeskAssignment.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_select_desk_assignments_by_desk_id(session: AsyncSession, desk_id: int):
    query = select(DeskAssignment).where(DeskAssignment.desk_id == desk_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_update_desk_assignment_days(session: AsyncSession, user_id: int, desk_id: int, **weekdays):
    try:
        await session.execute(
            update(DeskAssignment).
            where(
                DeskAssignment.user_id == user_id,
                DeskAssignment.desk_id == desk_id
            ).
            values(
                is_monday=weekdays.get('is_monday', False),
                is_tuesday=weekdays.get('is_tuesday', False),
                is_wednesday=weekdays.get('is_wednesday', False),
                is_thursday=weekdays.get('is_thursday', False),
                is_friday=weekdays.get('is_friday', False)
            )
        )
        await session.commit()
        return "Desk assignment successfully updated."
    except SQLAlchemyError as e:
        await session.rollback()
        raise DeskBookerError(f"Failed to update desk assignment: {str(e)}")


async def orm_delete_desk_assignment(session: AsyncSession, user_id: int, desk_id: int):
    try:
        await session.execute(
            delete(DeskAssignment).
            where(
                DeskAssignment.user_id == user_id,
                DeskAssignment.desk_id == desk_id
            )
        )
        await session.commit()
        return "Desk assignment successfully deleted."
    except SQLAlchemyError as e:
        await session.rollback()
        raise DeskBookerError(f"Failed to delete desk assignment: {str(e)}")


#* Booking's ORM queries
async def orm_insert_booking(
    session: AsyncSession,
    telegram_id: int,
    desk_id: int,
    room_id: int,
    date: date) -> str:
    query = select(Booking).where(
        Booking.telegram_id == telegram_id,
        Booking.desk_id == desk_id,
        Booking.date == date)
    result = await session.execute(query)
    booking = result.first()
    if booking:
        raise DeskBookerError("A booking for this desk already exists.")
    else:
        new_booking = Booking(
                telegram_id=telegram_id,
                desk_id=desk_id,
                room_id=room_id,
                date=date)
        session.add(new_booking)
        try:
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()  # Rollback in case of any commit failure
            raise Exception("Failed to insert booking into the database.") from e

        return "Booking successfully made."


async def orm_select_bookings_by_telegram_id_joined(session: AsyncSession, telegram_id: int):
    query = select(Booking).filter(Booking.telegram_id == telegram_id).options(joinedload(Booking.desk).joinedload(Desk.room)).order_by(Booking.date)
    result = await session.execute(query)
    return result.scalars().all()


# Returns bookings from today onwards joined with desk and room data
async def orm_select_bookings_by_telegram_id_joined_from_today(session: AsyncSession, telegram_id: int):
    query = select(Booking).filter(Booking.telegram_id == telegram_id, Booking.date >= date.today()).options(joinedload(Booking.desk).joinedload(Desk.room)).order_by(Booking.date)
    result = await session.execute(query)
    return result.scalars().all()


#* In computer terms, we changed the way we asked for the data. We made sure that when we asked for the bookings (Booking), we got not only the bookings themselves but also the user who made each booking (User), and where the booking is for (Desk and Room), all in one go. This is called "eager loading" – like eagerly bringing all the toys you need at once.
async def orm_select_bookings_by_room_id_joined_from_today(session: AsyncSession, room_id: int):
    query = select(Booking).filter(
        Booking.room_id == room_id, 
        Booking.date >= date.today()
    ).options(
        joinedload(Booking.desk).joinedload(Desk.room),
        joinedload(Booking.user)  # Eagerly load User relationship
    ).order_by(Booking.date)
    try:
        result = await session.execute(query)
        bookings = result.scalars().all()
        return bookings
    except Exception as e:
        raise e


async def orm_select_bookings_by_telegram_id(session: AsyncSession, telegram_id: int):
    query = select(Booking).where(Booking.telegram_id == telegram_id).order_by(Booking.date)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_select_booking_by_telegram_id_and_date(session: AsyncSession, telegram_id: int, date: date):
    query = select(Booking).where(Booking.telegram_id == telegram_id, Booking.date == date)
    result = await session.execute(query)
    return result.scalar()


async def orm_select_booking_by_telegram_id_and_date_selectinload(session: AsyncSession, telegram_id: int, date: date):
    query = select(Booking).options(selectinload(Booking.room), selectinload(Booking.desk)).where(Booking.telegram_id == telegram_id, Booking.date == date)
    result = await session.execute(query)
    return result.scalar()


async def orm_select_booking_by_desk_id_and_date(session: AsyncSession, desk_id: int, date: date):
    query = select(Booking).where(Booking.desk_id == desk_id, Booking.date == date)
    result = await session.execute(query)
    return result.scalar()


async def orm_select_bookings_by_desk_id(session: AsyncSession, desk_id: int):
    query = select(Booking).where(Booking.desk_id == desk_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_select_bookings_by_date(session: AsyncSession, date: date):
    query = select(Booking).where(Booking.date == date)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_booking_by_id(session: AsyncSession, booking_id: int):
    query = delete(Booking).where(Booking.id == booking_id)
    await session.execute(query)
    await session.commit()