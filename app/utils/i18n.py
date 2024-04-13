from fluent_compiler.bundle import FluentBundle

from fluentogram import FluentTranslator, TranslatorHub


def create_translator_hub() -> TranslatorHub:
    translator_hub = TranslatorHub(
        {
            "en": ("en",),
            "ru": ("ru", "en"),
        },
        [
            FluentTranslator(
                locale="en",
                translator=FluentBundle.from_files(
                    locale="en-US",
                    filenames=[
                        "app/locales/en/LC_MESSAGES/txt.ftl",
                        # "app/locales/ru/LC_MESSAGES/my_bookings_dialog.ftl",
                        ])),
            FluentTranslator(
                locale="ru",
                translator=FluentBundle.from_files(
                    locale="ru-RU",
                    filenames=[
                        "app/locales/ru/LC_MESSAGES/txt.ftl",
                        # "app/locales/ru/LC_MESSAGES/my_bookings_dialog.ftl",
                        ])),
        ],
    )
    return translator_hub

# To compile the translations, run the following command:
# i18n -ftl locales/en/LC_MESSAGES/booking_dialog.ftl -stub locales/stub.pyi