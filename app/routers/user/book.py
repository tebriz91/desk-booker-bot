from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from app.config_data.config import Config
from app.states.states import Booking
from app.routers.user.router import user_router


@user_router.message(Command('book'))
async def process_command_booking(message: Message,
                                  dialog_manager: DialogManager,
                                  config: Config):
    # Convert config data to a serializable format
    # And pass it to the dialog_data
    config_data = {
    'bot_operation_config': config.bot_operation.to_dict(),
    'bot_advanced_mode_config': config.bot_advanced_mode.to_dict(),
    }
    await dialog_manager.start(
        Booking.select_date,
        mode=StartMode.RESET_STACK,
        data=config_data,
    )