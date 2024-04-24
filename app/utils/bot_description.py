from aiogram import Bot


async def set_bot_description(bot: Bot) -> None:
    description = 'Press "Start" or Menu Button'
    # short_description = 'Desk Booker bot v.1.0'
    
    await bot.set_my_description(description)
    # await bot.set_my_short_description(short_description)