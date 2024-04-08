'''from aiogram import Router

from dialogs.booking import bot_menu_dialogs

def setup_all_dialogs(router: Router):
    for dialog in bot_menu_dialogs():
        router.include_router(dialog)'''