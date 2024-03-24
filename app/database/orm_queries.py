from datetime import date

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from database.models import User, Waitlist, Room, Desk, Booking

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

#* Waitlist's ORM queries
async def orm_insert_user_to_waitlist(
    session: AsyncSession,
    telegram_id: int,
    telegram_name: str,
    first_name: str = None,
    last_name: str = None):
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

#* Booking's ORM queries
async def orm_insert_booking(
    session: AsyncSession,
    telegram_id: int,
    desk_id: int,
    room_id: int,
    date: date):
    query = select(Booking).where(
        Booking.telegram_id == telegram_id,
        Booking.desk_id == desk_id,
        Booking.date == date)
    result = await session.execute(query)
    booking = result.first()
    if booking is None:
        new_booking = Booking(
                telegram_id=telegram_id,
                desk_id=desk_id,
                room_id=room_id,
                date=date)
        session.add(new_booking)
        await session.commit()
    else:
        raise Exception

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