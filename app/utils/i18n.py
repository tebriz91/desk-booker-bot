from dataclasses import dataclass
from pathlib import Path

from fluent_compiler.bundle import FluentBundle # type: ignore
from fluentogram import FluentTranslator, TranslatorHub # type: ignore


# Get the directory where the script is located
base_dir = Path(__file__).resolve().parent.parent.parent

# Define the file paths relative to the base path
en_file_path = base_dir / 'app' / 'locales' / 'en' / 'LC_MESSAGES' / 'txt.ftl'
ru_file_path = base_dir / 'app' / 'locales' / 'ru' / 'LC_MESSAGES' / 'txt.ftl'


@dataclass
class Translator:
    global_lang: str = "en"
    
    translator_hub: TranslatorHub = TranslatorHub(
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
                        en_file_path,
                        # "app/locales/ru/LC_MESSAGES/txt.ftl",
                        ])),
            FluentTranslator(
                locale="ru",
                translator=FluentBundle.from_files(
                    locale="ru-RU",
                    filenames=[
                        ru_file_path,
                        # "app/locales/ru/LC_MESSAGES/txt.ftl",
                        ])),
        ],
        root_locale="en",
    )

# To compile the translations, run the following command:
# i18n -ftl locales/en/LC_MESSAGES/txt.ftl -stub locales/stub.pyi