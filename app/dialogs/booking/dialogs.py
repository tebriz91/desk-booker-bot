from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Select,
    Column,
    Row,
    Cancel,
    Back,
)
from aiogram_dialog.widgets.text import Const, Format

from states.states import Booking

from misc.const.button_labels import ButtonLabel
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
        Const('Select a date'),
        Column(
            Select(
                Format('{item}'),
                id='date',
                items='dates',
                item_id_getter=lambda item: item,
                on_click=selected_date,
            ),
        ),
        Cancel(Format(ButtonLabel.CANCEL.value)),
        state=Booking.select_date,
        getter=get_dates,
    ),
    Window(
        Format('Selected date: {dialog_data[date]}. Now select a room.'),
        Column(
            Select(
                Format('{item}'),
                id='room_name',
                items='rooms',
                item_id_getter=lambda item: item,
                on_click=selected_room,
            ),
        ),
        Row(
            Back(Format(ButtonLabel.BACK.value)),
            Cancel(Format(ButtonLabel.CANCEL.value)),
        ),
        getter=get_rooms,
        state=Booking.select_room,
    ),
    Window(
        Format('''
               Selected date: {dialog_data[date]}, room: {dialog_data[room_name]}. Now select a desk according to the <a href='{dialog_data[room_plan_url]}'>room plan</a>.
               '''),
        Column(
            Select(
                Format('{item}'),
                id='desk_name',
                items='desks',
                item_id_getter=lambda item: item,
                on_click=selected_desk,
            ),
        ),
        Row(
            Back(Format(ButtonLabel.BACK.value)),
            Cancel(Format(ButtonLabel.CANCEL.value)),
        ),
        getter=get_desks,
        state=Booking.select_desk,
    ),
)