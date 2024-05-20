from typing import List, Tuple, Dict, Any


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


# Data Set 1
TEST_USERS_1: List[Tuple[int, str]] = [
    (123456789, "harry_potter"),
    (234567890, "hermione_granger"),
    (345678901, "ron_weasley"),
    (456789012, "albus_dumbledore"),
    (567890123, "severus_snape"),
    (678901234, "draco_malfoy"),
    (789012345, "tom_riddle"),
    (890123456, "ginny_weasley"),
]


TEST_ROOMS_1: List[str] = [
    "Gryffindor Room",
    "Slytherin Room",
    "Ravenclaw Room",
    "Hufflepuff Room",
    "Room of Requirement",
    "Great Hall",
]


TEST_DESKS_1: Dict[str, List[str]] = {
    "Gryffindor Room": [
        "Desk 1", "Desk 2", "Desk 3", "Desk 4", "Desk 5",
    ],
    "Slytherin Room": [
        "Desk 6", "Desk 7", "Desk 8", "Desk 9", "Desk 10",
    ],
    "Ravenclaw Room": [
        "Desk 11", "Desk 12", "Desk 13", "Desk 14", "Desk 15",
    ],
    "Hufflepuff Room": [
        "Desk 16", "Desk 17", "Desk 18", "Desk 19", "Desk 20",
    ],
    "Room of Requirement": [
        "Desk 21", "Desk 22", "Desk 23", "Desk 24", "Desk 25",
    ],
    "Great Hall": [
        "Desk 26", "Desk 27", "Desk 28", "Desk 29", "Desk 30",
    ],
}


# Data Set 2
TEST_USERS_2: List[Tuple[int, str]] = [
    (223456789, "james_potter"),
    (334567890, "lily_potter"),
    (445678901, "sirius_black"),
    (667890123, "peter_pettigrew"),
    (778901234, "нарцисса_мэлфой"),
    (889012345, "lucius_malfoy"),
    (990123456, "bellatrix_lestrange"),
    (112233445, "аластор_муди"),
    (223344556, "arthur_weasley"),
]


TEST_ROOMS_2: List[str] = [
    "Dumbledore's Office",
    "Snape's Dungeon",
    "Moaning Myrtle's Bathroom",
    "Forbidden Forest",
    "Hagrid's Hut",
    "Astronomy Tower",
    "Библиотека",
    "Квиддичное Поле",
]


TEST_DESKS_2: Dict[str, List[str]] = {
    "Dumbledore's Office": [
        "Desk A1", "Desk B2", "Desk C3", "Desk D4", "Desk E5"
    ],
    "Snape's Dungeon": [
        "Desk F6", "Desk G7", "Desk H8", "Desk I9", "Desk J10"
    ],
    "Moaning Myrtle's Bathroom": [
        "Desk K11", "Desk L12", "Desk M13", "Desk N14", "Desk O15"
    ],
    "Forbidden Forest": [
        "Desk P16", "Desk Q17", "Desk R18", "Desk S19", "Desk T20"
    ],
    "Hagrid's Hut": [
        "Desk U21", "Desk V22", "Desk W23", "Desk X24", "Desk Y25"
    ],
    "Astronomy Tower": [
        "Desk Z26", "Desk AA27", "Desk BB28", "Desk CC29", "Desk DD30"
    ],
    "Библиотека": [
        "Стол 1", "Стол 2", "Стол 3", "Стол 4", "Стол 5"
    ],
    "Квиддичное Поле": [
        "Стол 6", "Стол 7", "Стол 8", "Стол 9", "Стол 10"
    ],
}


# Data Set 3
TEST_USERS_3: List[Tuple[int, str]] = [
    (767890123, "перси_уизли"),
    (190123456, "флер_делакур"),
    (312233445, "виктор_крам"),
    (423344556, "кедрик_диггори"),
    (534455667, "оливандер"),
    (645566778, "филч"),
    (756677889, "профессор_макгонагалл"),
    (867788900, "профессор_локон"),
    (978899011, "профессор_флитвик"),
    (189900122, "профессор_квиррел"),
    (290011233, "профессор_трелони"),
    (401122344, "профессор_снейп"),
    (512233455, "профессор_лупин"),
    (623344566, "профессор_муглорн"),
]


TEST_ROOMS_3: List[str] = [
    "Сарай",
    "Домик на дереве",
    "Поле для квиддича",
    "Пруд",
    "Кухня",
    "Гараж",
    "Библиотека",
    "Комната для гостей",
    "Комната для игр",
    "Комната для чтения",
    "Комната для медитации",
    "Комната для сна",
    "Комната для работы",
    "Комната для отдыха",
]

TEST_DESKS_3: Dict[str, List[str]] = {
    "Сарай": [
        "Столярный верстак", "Рабочий стол", "Стол мастера", "Деревянный стол", "Стол с инструментами"
    ],
    "Домик на дереве": [
        "Детский стол", "Игровой столик", "Стол с игрушками", "Секретный стол", "Тайный стол"
    ],
    "Поле для квиддича": [
        "Тренерский стол", "Стол для инвентаря", "Барный стол великана", "Обзорный стол", "Тактический стол"
    ],
    "Пруд": [
        "Рыбацкий стол", "Пикниковый стол", "Стол на причале", "Стол с удочками", "Стол у воды"
    ],
    "Кухня": [
        "Кухонный остров", "Приготовительный стол", "Подставка для ножей", "Барный стол", "Сервировочный стол"
    ],
    "Гараж": [
        "Механический стол", "Стол для инструментов", "Рабочая поверхность", "Автомобильный стол", "Стол для ремонта"
    ],
    "Библиотека": [
        "Читательский стол", "Стол с книгами", "Круговой стол", "Письменный стол", "Стол для чтения"
    ],
    "Комната для гостей": [
        "Гостевой стол", "Стол с угощениями", "Чайный стол", "Стол для бесед", "Обеденный стол"
    ],
    "Комната для игр": [
        "Игровой стол", "Стол с пазлами", "Конструкторский стол", "Стол для настольных игр", "Игрушечный стол"
    ],
    "Комната для чтения": [
        "Стол для читателя", "Стол для книг", "Комфортный стол", "Уютный стол", "Стол с лампой"
    ],
    "Комната для медитации": [
        "Стол для свечей", "Стол для медитации", "Стол для расслабления", "Тихий стол", "Спокойный стол"
    ],
    "Комната для сна": [
        "Ночной столик", "Стол у кровати", "Спальный стол", "Угловой стол", "Мини столик"
    ],
    "Комната для работы": [
        "Офисный стол", "Стол для работы", "Стол с компьютером", "Стол с документами", "Стол руководителя"
    ],
    "Комната для отдыха": [
        "Рекреационный стол", "Стол для напитков", "Стол для закусок", "Книжный столик", "Стол с играми"
    ],
}


TEST_DATA = [
    (TEST_USERS_1, TEST_ROOMS_1, TEST_DESKS_1),
    (TEST_USERS_2, TEST_ROOMS_2, TEST_DESKS_2),
    (TEST_USERS_3, TEST_ROOMS_3, TEST_DESKS_3),
]