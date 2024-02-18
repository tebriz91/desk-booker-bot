from aiogram import Bot
from aiogram.types import BotCommand

from lexicon.lexicon_en import LEXICON_COMMANDS_EN


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command=command,
            description=description
        ) for command, description in LEXICON_COMMANDS_EN.items()
    ]
    await bot.set_my_commands(main_menu_commands)