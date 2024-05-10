from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from fluentogram import TranslatorHub # type: ignore

from app.utils.i18n import Translator

class TranslatorRunnerMiddleware(BaseMiddleware):
    
    
    def __init__(self, translator: Translator) -> None:
        """Initialize the TranslatorRunnerMiddleware.

        This method is called when creating an instance of the middleware.
        It sets up the middleware with the provided `translator` for language
        translation.

        :param translator: Translator: An instance of the Translator class that
        handles bot localization.
        """
        super().__init__()
        self.translator = translator
        self.lang = translator.global_lang    
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Awaitable[Any]:

        user: User = data.get('event_from_user')

        if user is None:
            return await handler(event, data)

        hub: TranslatorHub = self.translator.translator_hub
        data['i18n'] = hub.get_translator_by_locale(locale=user.language_code)

        return await handler(event, data)