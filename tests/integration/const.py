from typing import List, Tuple, Dict, Any

from app.database.models import User, Room, Desk

# TODO: Refactor to use a Config class instead of a dictionary
BOT_CONFIGURATIONS: Dict[str, Dict[str, Any]] = {
    "default": {},
    "1": {
        "bot_operation": {
            "advanced_mode": True,
            "num_days": 10,
            "exclude_weekends": False,
            "date_format": "%Y-%m-%d (%a)",
        },
        "bot_advanced_mode": {
            "standard_access_days": 1,
        },
    },
    "2": {
        "bot_operation": {
            "advanced_mode": True,
            "num_days": 5,
            "exclude_weekends": True,
            "date_format": "%m/%d/%Y (%a)",
            "date_format_short": "%m/%d/%Y",
        },
        "bot_advanced_mode": {
            "standard_access_days": 3,
        },
    },
    "3": {
        "bot_operation": {
            "advanced_mode": True,
            "num_days": 7,
            "exclude_weekends": False,
            "date_format": "%d.%m.%Y (%a)",
            "date_format_short": "%d.%m.%Y",
        },
        "bot_advanced_mode": {
            "standard_access_days": 5,
        },
    },
}


DATA_SET_0: Tuple[List[User], List[Room], List[Desk]] = (
    [
        User(telegram_id=123456789, telegram_name="harry_potter"),
        User(telegram_id=234567890, telegram_name="hermione_granger"),
        User(telegram_id=345678901, telegram_name="ron_weasley"),
        User(telegram_id=456789012, telegram_name="albus_dumbledore"),
        User(telegram_id=567890123, telegram_name="severus_snape"),
        User(telegram_id=678901234, telegram_name="draco_malfoy"),
        User(telegram_id=789012345, telegram_name="tom_riddle"),
        User(telegram_id=890123456, telegram_name="ginny_weasley"),
    ],
    [
        Room(id=1, name="Gryffindor Room"),
        Room(id=2, name="Slytherin Room"),
        Room(id=3, name="Ravenclaw Room"),
        Room(id=4, name="Hufflepuff Room"),
        Room(id=5, name="Room of Requirement"),
        Room(id=6, name="Great Hall"),
    ],
    [
        Desk(id=1, name="Desk 1", room_id=1),
        Desk(id=2, name="Desk 2", room_id=1),
        Desk(id=3, name="Desk 3", room_id=1),
        Desk(id=4, name="Desk 4", room_id=1),
        Desk(id=5, name="Desk 5", room_id=1),
        Desk(id=6, name="Desk 6", room_id=2),
        Desk(id=7, name="Desk 7", room_id=2),
        Desk(id=8, name="Desk 8", room_id=2),
        Desk(id=9, name="Desk 9", room_id=2),
        Desk(id=10, name="Desk 10", room_id=2),
        Desk(id=11, name="Desk 11", room_id=3),
        Desk(id=12, name="Desk 12", room_id=3),
        Desk(id=13, name="Desk 13", room_id=3),
        Desk(id=14, name="Desk 14", room_id=3),
        Desk(id=15, name="Desk 15", room_id=3),
        Desk(id=16, name="Desk 16", room_id=4),
        Desk(id=17, name="Desk 17", room_id=4),
        Desk(id=18, name="Desk 18", room_id=4),
        Desk(id=19, name="Desk 19", room_id=4),
        Desk(id=20, name="Desk 20", room_id=4),
        Desk(id=21, name="Desk 21", room_id=5),
        Desk(id=22, name="Desk 22", room_id=5),
        Desk(id=23, name="Desk 23", room_id=5),
        Desk(id=24, name="Desk 24", room_id=5),
        Desk(id=25, name="Desk 25", room_id=5),
        Desk(id=26, name="Desk 26", room_id=6),
        Desk(id=27, name="Desk 27", room_id=6),
        Desk(id=28, name="Desk 28", room_id=6),
        Desk(id=29, name="Desk 29", room_id=6),
        Desk(id=30, name="Desk 30", room_id=6),
    ],
)
    

DATA_SET_1: Tuple[List[User], List[Room], List[Desk]] = (
    [
        User(telegram_id=223456789, telegram_name="james_potter"),
        User(telegram_id=334567890, telegram_name="lily_potter"),
        User(telegram_id=445678901, telegram_name="sirius_black"),
        User(telegram_id=667890123, telegram_name="peter_pettigrew"),
        User(telegram_id=778901234, telegram_name="нарцисса_мэлфой"),
        User(telegram_id=889012345, telegram_name="lucius_malfoy"),
        User(telegram_id=990123456, telegram_name="bellatrix_lestrange"),
        User(telegram_id=112233445, telegram_name="аластор_муди"),
        User(telegram_id=223344556, telegram_name="arthur_weasley"),
    ],
    [
        Room(id=1, name="Dumbledore's Office"),
        Room(id=2, name="Snape's Dungeon"),
        Room(id=3, name="Moaning Myrtle's Bathroom"),
        Room(id=4, name="Forbidden Forest"),
        Room(id=5, name="Hagrid's Hut"),
        Room(id=6, name="Astronomy Tower"),
        Room(id=7, name="Библиотека"),
        Room(id=8, name="Квиддичное Поле"),
    ],
    [
        Desk(id=1, name="Desk A1", room_id=1),
        Desk(id=2, name="Desk B2", room_id=1),
        Desk(id=3, name="Desk C3", room_id=1),
        Desk(id=4, name="Desk D4", room_id=1),
        Desk(id=5, name="Desk E5", room_id=1),
        Desk(id=6, name="Desk F6", room_id=2),
        Desk(id=7, name="Desk G7", room_id=2),
        Desk(id=8, name="Desk H8", room_id=2),
        Desk(id=9, name="Desk I9", room_id=2),
        Desk(id=10, name="Desk J10", room_id=2),
        Desk(id=11, name="Desk K11", room_id=3),
        Desk(id=12, name="Desk L12", room_id=3),
        Desk(id=13, name="Desk M13", room_id=3),
        Desk(id=14, name="Desk N14", room_id=3),
        Desk(id=15, name="Desk O15", room_id=3),
        Desk(id=16, name="Desk P16", room_id=4),
        Desk(id=17, name="Desk Q17", room_id=4),
        Desk(id=18, name="Desk R18", room_id=4),
        Desk(id=19, name="Desk S19", room_id=4),
        Desk(id=20, name="Desk T20", room_id=4),
        Desk(id=21, name="Desk U21", room_id=5),
        Desk(id=22, name="Desk V22", room_id=5),
        Desk(id=23, name="Desk W23", room_id=5),
        Desk(id=24, name="Desk X24", room_id=5),
        Desk(id=25, name="Desk Y25", room_id=5),
        Desk(id=26, name="Desk Z26", room_id=6),
        Desk(id=27, name="Desk AA27", room_id=6),
        Desk(id=28, name="Desk BB28", room_id=6),
        Desk(id=29, name="Desk CC29", room_id=6),
        Desk(id=30, name="Desk DD30", room_id=6),
        Desk(id=31, name="Стол 1", room_id=7),
        Desk(id=32, name="Стол 2", room_id=7),
        Desk(id=33, name="Стол 3", room_id=7),
        Desk(id=34, name="Стол 4", room_id=7),
        Desk(id=35, name="Стол 5", room_id=7),
        Desk(id=36, name="Стол 6", room_id=8),
        Desk(id=37, name="Стол 7", room_id=8),
        Desk(id=38, name="Стол 8", room_id=8),
        Desk(id=39, name="Стол 9", room_id=8),
        Desk(id=40, name="Стол 10", room_id=8),
    ],
)


DATA_SET_2: Tuple[List[User], List[Room], List[Desk]] = (
    [
        User(telegram_id=767890123, telegram_name="перси_уизли"),
        User(telegram_id=190123456, telegram_name="флер_делакур"),
        User(telegram_id=312233445, telegram_name="виктор_крам"),
        User(telegram_id=423344556, telegram_name="кедрик_диггори"),
        User(telegram_id=534455667, telegram_name="оливандер"),
        User(telegram_id=645566778, telegram_name="филч"),
        User(telegram_id=756677889, telegram_name="профессор_макгонагалл"),
        User(telegram_id=867788900, telegram_name="профессор_локон"),
        User(telegram_id=978899011, telegram_name="профессор_флитвик"),
        User(telegram_id=189900122, telegram_name="профессор_квиррел"),
        User(telegram_id=290011233, telegram_name="профессор_трелони"),
        User(telegram_id=401122344, telegram_name="профессор_снейп"),
        User(telegram_id=512233455, telegram_name="профессор_лупин"),
        User(telegram_id=623344566, telegram_name="профессор_муглорн"),
    ],
    [
        Room(id=1, name="Сарай"),
        Room(id=2, name="Домик на дереве"),
        Room(id=3, name="Поле для квиддича"),
        Room(id=4, name="Пруд"),
        Room(id=5, name="Кухня"),
        Room(id=6, name="Гараж"),
        Room(id=7, name="Библиотека"),
        Room(id=8, name="Комната для гостей"),
        Room(id=9, name="Комната для игр"),
        Room(id=10, name="Комната для чтения"),
        Room(id=11, name="Комната для медитации"),
        Room(id=12, name="Комната для сна"),
        Room(id=13, name="Комната для работы"),
        Room(id=14, name="Комната для отдыха"),
    ],
    [
        Desk(id=1, name="Столярный верстак", room_id=1),
        Desk(id=2, name="Рабочий стол", room_id=1),
        Desk(id=3, name="Стол мастера", room_id=1),
        Desk(id=4, name="Деревянный стол", room_id=1),
        Desk(id=5, name="Стол с инструментами", room_id=1),
        Desk(id=6, name="Детский стол", room_id=2),
        Desk(id=7, name="Игровой столик", room_id=2),
        Desk(id=8, name="Стол с игрушками", room_id=2),
        Desk(id=9, name="Секретный стол", room_id=2),
        Desk(id=10, name="Тайный стол", room_id=2),
        Desk(id=11, name="Тренерский стол", room_id=3),
        Desk(id=12, name="Стол для инвентаря", room_id=3),
        Desk(id=13, name="Барный стол великана", room_id=3),
        Desk(id=14, name="Обзорный стол", room_id=3),
        Desk(id=15, name="Тактический стол", room_id=3),
        Desk(id=16, name="Рыбацкий стол", room_id=4),
        Desk(id=17, name="Пикниковый стол", room_id=4),
        Desk(id=18, name="Стол на причале", room_id=4),
        Desk(id=19, name="Стол с удочками", room_id=4),
        Desk(id=20, name="Стол у воды", room_id=4),
        Desk(id=21, name="Кухонный остров", room_id=5),
        Desk(id=22, name="Приготовительный стол", room_id=5),
        Desk(id=23, name="Подставка для ножей", room_id=5),
        Desk(id=24, name="Барный стол", room_id=5),
        Desk(id=25, name="Сервировочный стол", room_id=5),
        Desk(id=26, name="Механический стол", room_id=6),
        Desk(id=27, name="Стол для инструментов", room_id=6),
        Desk(id=28, name="Рабочая поверхность", room_id=6),
        Desk(id=29, name="Автомобильный стол", room_id=6),
        Desk(id=30, name="Стол для ремонта", room_id=6),
        Desk(id=31, name="Читательский стол", room_id=7),
        Desk(id=32, name="Стол с книгами", room_id=7),
        Desk(id=33, name="Круговой стол", room_id=7),
        Desk(id=34, name="Письменный стол", room_id=7),
        Desk(id=35, name="Стол для чтения", room_id=7),
        Desk(id=36, name="Гостевой стол", room_id=8),
        Desk(id=37, name="Стол с угощениями", room_id=8),
        Desk(id=38, name="Чайный стол", room_id=8),
        Desk(id=39, name="Стол для бесед", room_id=8),
        Desk(id=40, name="Обеденный стол", room_id=8),
        Desk(id=41, name="Игровой стол", room_id=9),
        Desk(id=42, name="Стол с пазлами", room_id=9),
        Desk(id=43, name="Конструкторский стол", room_id=9),
        Desk(id=44, name="Стол для настольных игр", room_id=9),
        Desk(id=45, name="Игрушечный стол", room_id=9),
        Desk(id=46, name="Стол для читателя", room_id=10),
        Desk(id=47, name="Стол для книг", room_id=10),
        Desk(id=48, name="Комфортный стол", room_id=10),
        Desk(id=49, name="Уютный стол", room_id=10),
        Desk(id=50, name="Стол с лампой", room_id=10),
        Desk(id=51, name="Стол для свечей", room_id=11),
        Desk(id=52, name="Стол для медитации", room_id=11),
        Desk(id=53, name="Стол для расслабления", room_id=11),
        Desk(id=54, name="Тихий стол", room_id=11),
        Desk(id=55, name="Спокойный стол", room_id=11),
        Desk(id=56, name="Ночной столик", room_id=12),
        Desk(id=57, name="Стол у кровати", room_id=12),
        Desk(id=58, name="Спальный стол", room_id=12),
        Desk(id=59, name="Угловой стол", room_id=12),
        Desk(id=60, name="Мини столик", room_id=12),
        Desk(id=61, name="Офисный стол", room_id=13),
        Desk(id=62, name="Стол для работы", room_id=13),
        Desk(id=63, name="Стол с компьютером", room_id=13),
        Desk(id=64, name="Стол с документами", room_id=13),
        Desk(id=65, name="Стол руководителя", room_id=13),
        Desk(id=66, name="Рекреационный стол", room_id=14),
        Desk(id=67, name="Стол для напитков", room_id=14),
        Desk(id=68, name="Стол для закусок", room_id=14),
        Desk(id=69, name="Книжный столик", room_id=14),
        Desk(id=70, name="Стол с играми", room_id=14),
    ],
)


TEST_DATA: List[Tuple[List[User], List[Room], List[Desk]]] = [
    DATA_SET_0,
    DATA_SET_1,
    DATA_SET_2,
]