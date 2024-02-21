from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Room, Desk, Booking

#* User's ORM queries
async def orm_insert_user(session: AsyncSession, data: dict):
    object = User(
        telegram_id=data["telegram_id"],
        telegram_name=data["telegram_name"]
    )
    session.add(object)
    await session.commit()
    
async def orm_select_users(session: AsyncSession):
    query = select(User)
    result = await session.execute(query)
    return result.scalars().all()

#* Room's ORM queries
async def orm_insert_room(session: AsyncSession, data: dict):
    object = Room(name=data["name"])
    session.add(object)
    await session.commit()

async def orm_select_rooms(session: AsyncSession):
    query = select(Room)
    result = await session.execute(query)
    return result.scalars().all()

#* Desk's ORM queries
async def orm_insert_desk(session: AsyncSession, data: dict):
    object = Desk(
        room_id=data["room_id"],
        name=data["name"]
    )
    session.add(object)
    await session.commit()

async def orm_select_desk_id_by_name(session: AsyncSession, desk_name: str):
    query = select(Desk.id).where(Desk.name == desk_name)
    result = await session.execute(query)
    return result.scalar_one()

async def orm_select_desks_by_room_id(session: AsyncSession, room_id: int):
    query = select(Desk).where(Desk.room_id == room_id)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_select_desks_by_room_name(session: AsyncSession, room_name: str):
    query = select(Desk).join(Room).where(Room.name == room_name)
    result = await session.execute(query)
    return result.scalars().all()

#* Booking's ORM queries
async def orm_insert_booking(session: AsyncSession, data: dict):
    object = Booking(
        telegram_id=data["telegram_id"],
        desk_id=data["desk_id"],
        date=data["date"]
    )
    session.add(object)
    await session.commit()

async def orm_select_bookings_by_user_id(session: AsyncSession, telegram_id: int):
    query = select(Booking).where(Booking.telegram_id == telegram_id)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_select_bookings_by_desk_id(session: AsyncSession, desk_id: int):
    query = select(Booking).where(Booking.desk_id == desk_id)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_select_bookings_by_date(session: AsyncSession, date: str): #? check date type annotation
    query = select(Booking).where(Booking.date == date)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_delete_booking_by_id(session: AsyncSession, booking_id: int):
    query = delete(Booking).where(Booking.id == booking_id)
    await session.execute(query)
    await session.commit()