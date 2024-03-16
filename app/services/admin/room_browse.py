from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_get_room_data_by_name, orm_select_desks_by_room_id

async def room_browse_service(
    session: AsyncSession,
    room_name: str
    ) -> str:
    room_name = room_name.strip() # TODO: Remove if it's not needed
    try:
        # Retrieve room info (name, id, created, updated)
        room = await orm_get_room_data_by_name(session, room_name)
        room_availability_emoji = "☑️" if room.is_available else "🚫"
        room_info = f"<b>Room name</b>: {room.name}\n" \
                    f"<b>Room id</b>: {room.id}\n" \
                    f"<b>Room availability</b>: {room_availability_emoji}\n" \
                    f"<b>Room plan</b>: {room.plan}\n" \
                    f"<b>Room additional info</b>: {room.additional_info}\n" \
                    f"<b>Room created at</b>: {room.created_at}\n" \
                    f"<b>Room updated at</b>: {room.updated_at}\n" \
        # Retrieve desks info by room_id
        room_id = room.id
        desks = await orm_select_desks_by_room_id(session, room_id)
        try:
            # Check if there are any desks in the room
            if not desks:
                desks_info = "There are no desks in the room."
            else:
                # Make desks info string indented
                desks_info = f"<b>Desks</b>:\n"
                # Get enumerated list of desks
                for i, desk in enumerate(desks, start=1):
                    desk_availability_emoji = "☑️" if desk.is_available else "🚫"
                    desks_info += f"{i}. Desk name: {desk.name}\n" \
                                f"    id: {desk.id}\n" \
                                f"    availability: {desk_availability_emoji}\n" \
                                f"    additional info: {desk.additional_info}\n\n"
            result = f"{room_info}\n{desks_info}"
            return result
        except Exception as e:
            return f"Error: {e}"
    
    except Exception as e:
        return f"Error: {e}"