from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Cancel,
    Button,
)
from aiogram_dialog.widgets.text import Format

from states.states import Team

# from dialogs.team.handlers import (
#     ...
# )
from dialogs.team.getters import (
    get_team_info
)


team_dialog = Dialog(
    Window(
        Format(text='{empty}', when='empty'),
        Format(text='{no-info}', when='no-info'),
        Format(text='{team-info}', when='team-info'),
        Cancel(Format(text='{button-exit}'), when='button-exit'),
        state=Team.main_menu,
        getter=get_team_info,
    ),
)