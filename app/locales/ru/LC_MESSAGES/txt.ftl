<#-- common buttons -->
button-yes = Да
button-no = Нет
button-ok = 👌Ок
button-cancel = ❌Отмена
button-back = ⏪Назад
button-next = ⏩Вперед
button-main-menu = 🏠Главное меню
button-exit = 🏁Выход
button-confirm = ✅Подтвердить
button-toggle = 🔄Переключить


<#-- Common -->
select-date = Выберите дату:
selected-date = Дата: {$date}
select-room = Выберите кабинет:
selected-room = Кабинет: {$room_name}
select-desk = Выберите стол:
selected-desk = Стол: {$desk_name}
no-rooms = Нет доступных кабинетов


<#-- booking_dialog -->

<#-- booking_cheker.py -->
existing-booking = У вас есть 🚩бронь на дату: {$date} в кабинете: {$room_name}, стол: {$desk_name}

<#-- desk_assignment_cheker.py -->
desk-assignment = У вас есть 🔒постоянная бронь стола на этот день недели ({$weekday}). Посмотреть свои постоянные брони можно используя команду: /desk

<#-- handlers.py\selected_room() -->
there-are-no-desks = Сейчас в кабинете: {$room_name} нет доступных столов для бронирования на дату: {$date}

<#-- desk_booker.py -->
desk-booker-error = Упс... Кто-то только что забронировал этот стол. Пожалуйста, выберите другой
desk-booker-success = 🚩Забронирован стол: {$desk_name} в кабинете: {$room_name} на {$date}


<#-- my_bookings_handler -->

<#-- bookings_list_generator 
my-bookings-no-bookings = У вас нет забронированных столов
my-bookings-greeting = Ваши брони, {$telegram_name}:
my-bookings-date = <b>{$date}</b>
my-bookings-desk = Кабинет: {$room_name}, стол: {$desk_name}
my-bookings-bookedOn = <code>забронировано: {$booked_on}</code>
-->

<#-- bookings_list_generator -->
my-bookings-no-bookings = У вас нет 🚩забронированных столов
my-bookings-greeting = Ваши 🚩брони, {$telegram_name}:
my-bookings-list =
    <b>{$date}</b>
        Кабинет: {$room_name}, стол: {$desk_name}
        <code>забронировано: {$booked_on}</code>


<#-- cancel_bookings_dialog -->
no-bookings-to-cancel = У вас нет 🚩броней для отмены
select-booking-to-cancel = Выберите 🚩бронь для отмены:
bookings-to-cancel = {$date}, cтол: {$desk_name}, каб.: {$room_name}
cancel-booking-success = Бронь отмена


<#-- all_bookings_dialog -->
all-bookings-no-bookings = В кабинете нет 🚩забронированных столов
all-bookings-greeting = <b>🚩Забронированные столы в кабинете: {$room_name}</b>
all-bookings-date = <b>{$date}</b>
all-bookings-desk-user = Стол: {$desk_name}, {$telegram_name}
all-bookings-no-bookings-assignments = В кабинете нет 🚩забронированных столов и действующих 🔒постоянных броней
all-bookings-desk-assignments-first-line = <b>Действующие 🔒постоянные брони в кабинете: {$room_name}</b>
all-bookings-desk-assignments-weekday = <b>{$weekday}</b>


<#-- desk_dialog -->
desk-assignment-empty = У вас нет 🔒постоянных броней столов
desk-assignment-greeting = Ваши 🔒постоянные брони:
desk-assignment-info =
    <b>{$weekday}</b>
        Кабинет: <b>{$room_name}</b>, стол: <b>{$desk_name}</b>

desk-assignment-active =
    Бронь стола(-ов) сейчас ✅активна

    В случае отсутствия в офисе (отпуск, больничный и т.д.), нажмите кнопку ниже, чтобы освободить стол(ы) до вашего возвращения

desk-assignment-inactive =
    Бронь стола(-ов) сейчас ❌неактивна

    Если вы возвращаетесь в офис, нажмите кнопку ниже, чтобы активировать её