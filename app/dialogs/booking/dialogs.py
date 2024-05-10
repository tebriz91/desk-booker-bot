from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Select,
    Column,
    Row,
    Cancel,
    Back,
    ScrollingGroup,
    Group,
    Button,
)
from aiogram_dialog.widgets.text import Format, Multi

from app.states.states import Booking

from app.dialogs.booking.handlers import (
    selected_date,
    selected_room,
    selected_desk,
    selected_random_booking,
)
from app.dialogs.booking.getters import (
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
        ScrollingGroup(
            Select(
                Format('{item}'),
                id='room_name',
                items='rooms',
                item_id_getter=lambda item: item,
                on_click=selected_room,
            ),
            id='scroll_rooms',
            width=2,
            height=7,
            hide_on_single_page=True,
            when='rooms',
        ),
        Button(
            Format(text='{booking-random-button}'),
            id='random',
            on_click=selected_random_booking,
            when='booking-random-button',
        ),
        Row(
            Back(Format(text='{button-back}', when='button-back')),
            Cancel(Format(text='{button-exit}', when='button-exit')),
        ),
        getter=get_rooms,
        state=Booking.select_room,
    ),
    Window(
        # FIX: Replace '📋' with something
        Format(text='{selected-date}\n{selected-room}<a href="{room_plan}">📋</a>'),
        Format(text='{select-desk}'),
        ScrollingGroup(
            Select(
                Format('{item}'),
                id='desk_name',
                items='desks',
                item_id_getter=lambda item: item,
                on_click=selected_desk,
            ),
            id='scroll_rooms',
            width=2,
            height=5,
            hide_on_single_page=True,
        ),
        Row(
            Back(Format(text='{button-back}')),
            Cancel(Format(text='{button-exit}')),
        ),
        getter=get_desks,
        state=Booking.select_desk,
    ),
)