<#-- common buttons -->
button-yes = Yes
button-no = No
button-ok = 👌Ok
button-cancel = ❌Cancel
button-back = ⏪Back
button-next = ⏩Next
button-main-menu = 🏠Main Menu
button-exit = 🏁Exit
button-confirm = ✅Confirm
button-toggle = 🔄Toggle


<#-- Common -->
select-date = Select a date:
selected-date = Date: {$date}
select-room = Select a room:
selected-room = Room: {$room_name}
select-desk = Select a desk:
selected-desk = Desk: {$desk_name}
no-rooms = There are no rooms yet


<#-- booking_dialog -->

<#-- booking_cheker.py -->
existing-booking = You already have a 🚩booking on {$date} in room: {$room_name}, desk: {$desk_name}

<#-- desk_assignment_cheker.py -->
desk-assignment = You have an 🔒assigned desk for the selected weekday ({$weekday}). To see your permanent desk assinments use command: /desk

<#-- handlers.py\selected_room() -->
there-are-no-desks = For now there are no available desks in room: {$room_name} on: {$date}

<#-- desk_booker.py -->
desk-booker-error = Oops... Someone has booked the desk before you. Please select another desk
desk-booker-success = Successfully 🚩booked desk: {$desk_name} in room: {$room_name} for {$date}


<#-- my_bookings_handler -->

<#-- bookings_list_generator 
my-bookings-no-bookings = You have no bookings yet
my-bookings-greeting = Your bookings, {$telegram_name}:
my-bookings-date = <b>{$date}</b>
my-bookings-desk = Room: {$room_name}, Desk: {$desk_name}
my-bookings-bookedOn = <code>booked on: {$booked_on}</code>
-->

<#-- bookings_list_generator -->
my-bookings-no-bookings = You have no 🚩bookings yet
my-bookings-greeting = Your 🚩bookings, {$telegram_name}:
my-bookings-list =
    <b>{$date}</b>
        Room: {$room_name}, Desk: {$desk_name}
        <code>booked on: {$booked_on}</code>


<#-- cancel_bookings_dialog -->
no-bookings-to-cancel = You have no 🚩bookings to cancel
select-booking-to-cancel = Select a 🚩booking to cancel:
bookings-to-cancel = {$date}, Desk: {$desk_name}, Room: {$room_name}
cancel-booking-success = Booking has been cancelled


<#-- all_bookings_dialog -->
all-bookings-no-bookings = There are no 🚩bookings in this room yet
all-bookings-greeting = <b>🚩Bookings in Room: {$room_name}</b>
all-bookings-date = <b>{$date}</b>
all-bookings-desk-user = Desk: {$desk_name}, {$telegram_name}
all-bookings-no-bookings-assignments = There are no 🚩bookings and 🔒permanent desk assignments in this room yet
all-bookings-desk-assignments-first-line = <b>Active 🔒permanent desk assignments in Room: {$room_name}</b>
all-bookings-desk-assignments-weekday = {$weekday}


<#-- desk_dialog -->
desk-assignment-empty = You don't have an 🔒assigned desk
desk-assignment-greeting = Your 🔒desk assignment(s):
desk-assignment-info =
    <b>{$weekday}</b>
        Room: <b>{$room_name}</b>, Desk: <b>{$desk_name}</b>

desk-assignment-active =
    Desk assignment(s) is ✅active

    In case you are out of the office (vacation, sick leave, etc.), please press the button below to free the desk(s) until your return

desk-assignment-inactive =
    Desk assignment(s) is ❌inactive

    In case you are back to the office, press the button below to activate desk assignment(s)