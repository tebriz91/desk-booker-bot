from aiogram import Bot
from aiogram.types import BotCommand

from misc.const.main_menu import MainMenu

async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command=str(command),  # Uses the __str__ method of the Enum
            description=command.description
        ) for command in MainMenu
    ]
    await bot.set_my_commands(main_menu_commands)