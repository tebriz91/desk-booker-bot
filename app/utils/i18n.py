from fluent_compiler.bundle import FluentBundle # type: ignore

from fluentogram import FluentTranslator, TranslatorHub # type: ignore


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
                        # "app/locales/ru/LC_MESSAGES/txt.ftl",
                        ])),
            FluentTranslator(
                locale="ru",
                translator=FluentBundle.from_files(
                    locale="ru-RU",
                    filenames=[
                        "app/locales/ru/LC_MESSAGES/txt.ftl",
                        # "app/locales/ru/LC_MESSAGES/txt.ftl",
                        ])),
        ],
    )
    return translator_hub

# To compile the translations, run the following command:
# i18n -ftl locales/en/LC_MESSAGES/txt.ftl -stub locales/stub.pyi