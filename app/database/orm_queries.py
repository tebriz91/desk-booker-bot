from datetime import date
from typing import Optional

from sqlalchemy import Integer, String, and_, func, literal, not_, or_, select, update, delete
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


async def orm_select_is_out_of_office_by_telegram_id(
    session: AsyncSession,
    telegram_id: int):
    query = select(User.is_out_of_office).where(User.telegram_id == telegram_id)
    result = await session.execute(query)
    return result.scalar_one()

# Switching without deleting future bookings
async def orm_switch_is_out_of_office_by_telegram_id(
    session: AsyncSession,
    telegram_id: int):
    try:
        # Attempt to update the is_out_of_office status atomically
        query = (
            update(User).
            where(User.telegram_id == telegram_id).
            values(is_out_of_office=not_(User.is_out_of_office)).
            execution_options(synchronize_session="fetch")
        )
        result = await session.execute(query)
        if result.rowcount == 0:
            # No rows were updated, indicating the user does not exist
            raise ValueError(f"No user found with telegram_id {telegram_id}")
        await session.commit()
    except Exception as e:
        await session.rollback()  # Ensure transaction is rolled back in case of error
        raise  # Optionally re-raise or handle the exception differently


# Switching and deleting future bookings
async def orm_switch_is_out_of_office_by_telegram_id_and_clear_bookings(
    session: AsyncSession,
    telegram_id: int):
    try:
        # Check current out-of-office status before updating
        current_status_query = select(User.is_out_of_office).where(User.telegram_id == telegram_id)
        current_status_result = await session.execute(current_status_query)
        current_status = current_status_result.scalar_one()

        # Attempt to update the is_out_of_office status atomically
        query = (
            update(User).
            where(User.telegram_id == telegram_id).
            values(is_out_of_office=not_(current_status)).
            execution_options(synchronize_session="fetch")
        )
        update_result = await session.execute(query)
        if update_result.rowcount == 0:
            # No rows were updated, indicating the user does not exist
            raise ValueError(f"No user found with telegram_id {telegram_id}")
        await session.commit()

        # If changing from True to False, check desk assignments for deletions
        if current_status == True:
            # Find all desk assignments for this user
            desk_assignments_query = select(DeskAssignment.desk_id, DeskAssignment.weekday).where(DeskAssignment.telegram_id == telegram_id)
            desk_assignments_result = await session.execute(desk_assignments_query)
            desk_assignments = desk_assignments_result.all()

            for desk_id, assigned_weekday in desk_assignments:
                # Adjust the weekday to match SQL DOW (day of week) expectations
                sql_dow = (assigned_weekday.value + 1) % 7  # Shift by 1 to accommodate starting the week on Sunday

                # Delete future bookings on these desk IDs where booking date matches the assigned weekday
                delete_query = (
                    delete(Booking).
                    where(
                        Booking.desk_id == desk_id,
                        Booking.date >= date.today(),
                        func.extract('dow', Booking.date) == sql_dow  # Match the adjusted weekday value
                    )
                )
                await session.execute(delete_query)
            await session.commit()

    except Exception as e:
        await session.rollback()  # Ensure transaction is rolled back in case of error


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


async def orm_select_team_name_by_id(session: AsyncSession, team_id: int):
    query = select(Team.name).where(Team.id == team_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def orm_select_team_id_by_telegram_id(session: AsyncSession, telegram_id: int):
    query = select(UserRoleAssignment.team_id).where(UserRoleAssignment.telegram_id == telegram_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def orm_select_team_preferred_room_id(session: AsyncSession, team_id: int):
    query = select(Team.room_id).where(Team.id == team_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def orm_select_team_info_by_team_id(session: AsyncSession, team_id: int):
    # Query the Team table for the team name and room ID, than join with the Room table to get the room name, than join with the UserRoleAssignment table to get the user IDs and roles, and finally join with the User table to get the user names
    query = (
        select(
            Team.name.label("team_name"),
            Room.name.label("room_name"),
            User.telegram_name.label("user_name"),
            func.cast(UserRoleAssignment.role, String).label("role")  # Cast UserRole enum to String
        )
        .join(Room, Team.room_id == Room.id)
        .join(UserRoleAssignment, Team.id == UserRoleAssignment.team_id)
        .join(User, UserRoleAssignment.telegram_id == User.telegram_id)
        .where(Team.id == team_id)
        .order_by(UserRoleAssignment.role)  # Order by role for consistent output
    )
    result = await session.execute(query)
    return result.all()


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


async def orm_select_room_plan_by_room_id(session: AsyncSession, room_id: int):
    query = select(Room.plan).where(Room.id == room_id)
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

# Doesn't check if users for whom desks are assigned are out of office
async def orm_select_not_assigned_desks_by_desks_id_and_weekday(session: AsyncSession, desk_ids: list[int], weekday: Weekday):
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


async def orm_select_available_desks_by_desks_id_and_weekday(session: AsyncSession, desk_ids: list[int], weekday: Weekday):
    # Create a subquery that selects desk IDs assigned on the given weekday
    # and joins with the User table to check if the assigned user is out of office
    subquery = select(DeskAssignment.desk_id).join(User).where(
        DeskAssignment.weekday == weekday,
        DeskAssignment.desk_id.in_(desk_ids),
        User.is_out_of_office.is_(False)  # Only include desks where the user is not out of office
    ).distinct()

    # The main query selects desks by ID and excludes those in the subquery
    query = select(Desk).where(
        Desk.id.in_(desk_ids),
        ~Desk.id.in_(subquery)
    )
    result = await session.execute(query)
    return result.scalars().all()


async def orm_select_available_not_assigned_desks_by_room_id(session: AsyncSession, room_id: int, weekday: int):
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

    result = await session.execute(query)
    desks = result.scalars().all()

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
    # Directly query DeskAssignment by telegram_id and weekday, joining with User to access telegram_id
    query = select(DeskAssignment).join(User).where(
        User.telegram_id == telegram_id,
        DeskAssignment.weekday == weekday
    )
    result = await session.execute(query)
    desk_assignment = result.scalars().first()  # Using first() as we're now handling potentially multiple matches in one step
    
    if desk_assignment:
        return desk_assignment
    else:
        return None


async def orm_select_desk_assignments_by_telegram_id(session: AsyncSession, telegram_id: int):
    query = select(DeskAssignment).where(DeskAssignment.telegram_id == telegram_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_select_desk_assignments_by_telegram_id_selectinload(session: AsyncSession, telegram_id: int):
    query = select(DeskAssignment).options(selectinload(DeskAssignment.desk).selectinload(Desk.room)).where(DeskAssignment.telegram_id == telegram_id).order_by(DeskAssignment.weekday)
    result = await session.execute(query)
    return result.scalars().all()


# Returns desk assignments joined with desk and room data where the user is not out of office
async def orm_select_desk_assignments_by_room_id_selectinload(session: AsyncSession, room_id: int):
    query = select(DeskAssignment).join(User).options(
        selectinload(DeskAssignment.desk).selectinload(Desk.room),  # Eagerly load Desk and Room relationships
        selectinload(DeskAssignment.user)  # Eagerly load User relationship
    ).where(
        DeskAssignment.desk.has(Desk.room_id == room_id),  # Filter by room_id
        User.is_out_of_office.is_(False)  # Only include users that are not out of office
    ).order_by(DeskAssignment.weekday)
    
    try:
        result = await session.execute(query)
        return result.scalars().all()
    except Exception as e:
        raise e


async def orm_select_desk_assignments_by_team_id_selectinload(session: AsyncSession, team_id: int):
    query = (
        select(DeskAssignment)
        .join(Desk)
        .join(Room)
        .join(User)
        .options(
            selectinload(DeskAssignment.desk).selectinload(Desk.room),
            selectinload(DeskAssignment.user)
        )
        .where(
            User.user_role_assignments.any(UserRoleAssignment.team_id == team_id),
            User.is_out_of_office.is_(False)
        )
        .order_by(DeskAssignment.weekday)
    )

    try:
        result = await session.execute(query)
        return result.scalars().all()
    except Exception as e:
        raise e


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


async def orm_select_bookings_by_room_id_joined_from_today(session: AsyncSession, room_id: int):
    # Use an explicit select() construct for the desk_subquery
    desk_subquery = select(Desk.id).filter(Desk.room_id == room_id).subquery()
    
    # Now explicitly use select() when filtering by desk_id
    query = select(Booking).filter(
        Booking.desk_id.in_(select(Desk.id).filter(Desk.room_id == room_id)),  # Explicitly using select() here
        Booking.date >= date.today()
    ).options(
        joinedload(Booking.desk).joinedload(Desk.room),  # Eagerly load Desk and Room relationships
        joinedload(Booking.user)  # Eagerly load User relationship
    ).order_by(Booking.date)
    
    try:
        result = await session.execute(query)
        return result.scalars().all()
    except Exception as e:
        raise e


async def orm_select_bookings_by_team_id_joined_from_today(session: AsyncSession, team_id: int):
    query = (
        select(Booking)
        .join(Desk)
        .join(Room)
        .join(User)
        .options(
            joinedload(Booking.desk).joinedload(Desk.room),
            joinedload(Booking.user)
        )
        .where(
            User.user_role_assignments.any(UserRoleAssignment.team_id == team_id),
            Booking.date >= date.today()
        )
        .order_by(Booking.date)
    )

    try:
        result = await session.execute(query)
        return result.scalars().all()
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


async def orm_select_booking_by_telegram_id_and_date_selectinload(session: AsyncSession, telegram_id: int, booking_date: date) -> Optional[Booking]:
    query = select(Booking).options(
        selectinload(Booking.desk).selectinload(Desk.room),  # This chains loading of related Desk and its Room
        selectinload(Booking.user)  # Eagerly load the related User
    ).where(
        Booking.telegram_id == telegram_id,
        Booking.date == booking_date
    )
    try:
        result = await session.execute(query)
        return result.scalar()
    except Exception as e:
        raise e


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