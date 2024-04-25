from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Cancel,
    Button,
    Row,
    Back,
)
from aiogram_dialog.widgets.text import Format

from states.states import Team

from dialogs.team.handlers import (
    selected_team_bookings
)
from dialogs.team.getters import (
    get_team_info,
    get_team_bookings,
)


team_dialog = Dialog(
    Window(
        Format(text='{empty}', when='empty'),
        Format(text='{no-info}', when='no-info'),
        Format(text='{team-info}', when='team-info'),
        Button((Format(text='{team-button-bookings}')),
                   id='bookings',
                   when='team-info',
                   on_click=selected_team_bookings),
        Cancel(Format(text='{button-exit}'), when='button-exit'),
        state=Team.main_menu,
        getter=get_team_info,
    ),
    Window(
        Format(text='{empty}', when='empty'),
        Format(text='{error}', when='error'),
        Format(text='{bookings}', when='bookings'),
        Row(
            Back(Format(text='{button-back}'), when='button-back'),
            Cancel(Format(text='{button-exit}'), when='button-exit'),
        ),
        state=Team.view_bookings,
        getter=get_team_bookings,
    ),
)