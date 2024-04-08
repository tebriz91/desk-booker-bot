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


<#-- booking_dialog -->
select-date = Выберите дату:
selected-date = Дата: {$date}
select-room = Выберите кабинет:
selected-room = Кабинет: {$room_name}
select-desk = Выберите стол:

<#-- booking_cheker.py -->
existing-booking = У вас есть бронь на дату: {$date} в кабинете: {$room_name}, стол: {$desk_name}

<#-- desk_assignment_cheker.py -->
desk-assignment = У вас есть закрепленный стол на этот день недели ({$weekday})

<#-- handlers.py\selected_room() -->
there-are-no-desks = Сейчас в кабинете: {$room_name} нет доступных столов для бронирования на дату: {$date}

<#-- desk_booker.py -->
desk-booker-error = Упс... Кто-то только что забронировал этот стол. Пожалуйста, выберите другой
desk-booker-success = Забронирован стол: {$desk_name} в кабинете: {$room_name} на {$date}


<#-- my_bookings_handler -->

<#-- bookings_list_generator 
my-bookings-no-bookings = У вас нет забронированных столов
my-bookings-greeting = Ваши брони, {$telegram_name}:
my-bookings-date = <b>{$date}</b>
my-bookings-desk = Кабинет: {$room_name}, стол: {$desk_name}
my-bookings-bookedOn = <code>забронировано: {$booked_on}</code>
-->

<#-- bookings_list_generator -->
my-bookings-no-bookings = У вас нет забронированных столов
my-bookings-greeting = Ваши брони, {$telegram_name}:
my-bookings-list =
    <b>{$date}</b>
        Room: {$room_name}, Desk: {$desk_name}
        <code>booked on: {$booked_on}</code>


<#-- cancel_bookings_dialog -->
no-bookings-to-cancel = У вас нет броней для отмены
select-booking-to-cancel = Выберите бронь для отмены:
bookings-to-cancel = Стол: {$desk_name} в каб.: {$room_name} на {$date}
cancel-booking-success = Бронь отмена