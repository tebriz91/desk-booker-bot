from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Cancel,
    Button,
)
from aiogram_dialog.widgets.text import Format

from app.states.states import Desk

from app.dialogs.desk.handlers import (
    toggle_is_out_of_office_status,
)
from app.dialogs.desk.getters import (
    get_desk_assignment,
)


desk_dialog = Dialog(
    Window(
        Format(text='{desk-assignment-empty}',
               when='desk-assignment-empty'),
        Format(text='{desk-assignment-error}',
                when='desk-assignment-error'),
        Format(text='{desk-assignment-inactive}',
               when='desk-assignment-inactive'),
        Format(text='{desk-assignment-active}',
               when='desk-assignment-active'),
        Button((Format(text='{button-toggle}')),
               id='toggle',
               when='button-toggle',
               on_click=toggle_is_out_of_office_status),
        Cancel(Format(text='{button-exit}'),
               when='button-exit'),
        state=Desk.main_menu,
        getter=get_desk_assignment,
    ),
)