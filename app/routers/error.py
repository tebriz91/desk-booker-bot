'''
from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from app.utils.logger import Logger

error_router = Router()
logger = Logger('error')

@error_router.errors(F.update.message.as_('message'))
async def error_event(
        event: types.ErrorEvent, message: types.Message, state: FSMContext
) -> None:
    user_id = message.from_user.id  # type: ignore
    username = message.from_user.username  # type: ignore
    await state.clear()
    exception = event.exception
    logger.exception(
        f'Error: {type(exception).__name__}\nmessage: {exception}\n'
        f'from_user: {user_id}(username={username})\n'
        f'from_message: {message.text}'
    )
    await message.answer('What is going on?', reply_markup=types.ReplyKeyboardRemove())
'''