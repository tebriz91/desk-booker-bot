from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Select,
    Column,
    Row,
    Cancel,
    Back,
    Group,
    Button,
    ScrollingGroup,
)
from aiogram_dialog.widgets.text import Format, Multi, Const

from states.states import Booking

from dialogs.booking.handlers import (
    selected_date,
    selected_room,
    selected_desk,
)
from dialogs.booking.getters import (
    get_dates,
    get_rooms,
    get_desks,
)


booking_dialog = Dialog(
    Window(
        Format(text='{select-date}', when='dates'),
        Group(
            Column(
                Select(
                    Format('{item}'),
                    id='date',
                    items='dates',
                    item_id_getter=lambda item: item,
                    on_click=selected_date,
                ),
            ),
            Cancel(Format(text='{button-exit}')),
            when='dates',
        ),
        state=Booking.select_date,
        getter=get_dates,
    ),
    Window(
        Format(text='{no-rooms}', when='no-rooms'),
        Multi(
            Format(text='{selected-date}'),
            Format(text='{select-room}'),
            when='rooms',
        ),
        Group(
            Select(
                Format('{item}'),
                id='room_name',
                items='rooms',
                item_id_getter=lambda item: item,
                on_click=selected_room,
            ),
            width=1,
            when='rooms',
        ),
        Row(
            Back(Format(text='{button-back}', when='button-back')),
            Cancel(Format(text='{button-exit}', when='button-exit')),
        ),
        getter=get_rooms,
        state=Booking.select_room,
    ),
    Window(
        # TODO: Split desks into columns if there are too many
        # FIX: Replace '📋' with something
        Format(text='{selected-date}\n{selected-room}<a href="{room_plan}">📋</a>'),
        Format(text='{select-desk}'),
        Group(
            Select(
                Format('{item}'),
                id='desk_name',
                items='desks',
                item_id_getter=lambda item: item,
                on_click=selected_desk,
            ),
            width=1,
        ),
        Row(
            Back(Format(text='{button-back}')),
            Cancel(Format(text='{button-exit}')),
        ),
        getter=get_desks,
        state=Booking.select_desk,
    ),
)