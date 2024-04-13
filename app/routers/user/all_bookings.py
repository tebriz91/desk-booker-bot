from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from config_data.config import Config
from states.states import AllBookings
from routers.user.router import user_router


@user_router.message(Command('all_bookings'))
async def process_command_all_bookings(message: Message,
                                  dialog_manager: DialogManager,
                                  config: Config):
    # Convert config data to a serializable format
    # And pass it to the dialog_data
    config_data = {
    'bot_operation_config': config.bot_operation.to_dict(),
    }
    await dialog_manager.start(
        AllBookings.select_room,
        mode=StartMode.RESET_STACK,
        data=config_data,
    )