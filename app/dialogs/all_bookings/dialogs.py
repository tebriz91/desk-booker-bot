from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Select,
    Column,
    Row,
    Cancel,
    Back,
    Group,
)
from aiogram_dialog.widgets.text import Format

from states.states import AllBookings

from dialogs.all_bookings.handlers import (
    selected_room,
)
from dialogs.all_bookings.getters import (
    get_rooms,
    get_bookings,
)


all_bookings_dialog = Dialog(
    Window(
        Format(text='{no-rooms}', when='no-rooms'),
        Format(text='{select-room}', when='rooms'),
        Group(
            Column(
                Select(
                    # rooms = List[Tuple[room_id, room_name]]
                    Format('{item[1]}'), # room_name
                    id='room_name',
                    items='rooms',
                    item_id_getter=lambda item: item[0], # room_id
                    on_click=selected_room,
                ),
            ),
            Cancel(Format(text='{button-exit}')),
            when='rooms',
        ),
        state=AllBookings.select_room,
        getter=get_rooms,
    ),
    Window(
        Format(text='{bookings}'),
        Row(
            Back(Format(text='{button-back}')),
            Cancel(Format(text='{button-exit}')),
        ),
        state=AllBookings.view_bookings,
        getter=get_bookings,
    ),
)