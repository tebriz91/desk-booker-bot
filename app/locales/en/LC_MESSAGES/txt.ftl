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


<#-- booking_dialog -->
select-date = Select a date:
selected-date = Date: {$date}
select-room = Select a room:
selected-room = Room: {$room_name}
select-desk = Select a desk:

<#-- booking_cheker.py -->
existing-booking = You already have a booking on {$date} in room: {$room_name}, desk: {$desk_name}

<#-- desk_assignment_cheker.py -->
desk-assignment = You have an assigned desk for the selected weekday ({$weekday})

<#-- handlers.py\selected_room() -->
there-are-no-desks = For now there are no available desks in room: {$room_name} on: {$date}

<#-- desk_booker.py -->
desk-booker-error = Oops... Someone has booked the desk before you. Please select another desk
desk-booker-success = Successfully booked desk: {$desk_name} in room: {$room_name} for {$date}


<#-- my_bookings_handler -->

<#-- bookings_list_generator 
my-bookings-no-bookings = You have no bookings yet
my-bookings-greeting = Your bookings, {$telegram_name}:
my-bookings-date = <b>{$date}</b>
my-bookings-desk = Room: {$room_name}, Desk: {$desk_name}
my-bookings-bookedOn = <code>booked on: {$booked_on}</code>
-->

<#-- bookings_list_generator -->
my-bookings-no-bookings = You have no bookings yet
my-bookings-greeting = Your bookings, {$telegram_name}:
my-bookings-list =
    <b>{$date}</b>
        Room: {$room_name}, Desk: {$desk_name}
        <code>booked on: {$booked_on}</code>


<#-- cancel_bookings_dialog -->
no-bookings-to-cancel = You have no bookings to cancel
select-booking-to-cancel = Select a booking to cancel:
bookings-to-cancel = Desk: {$desk_name} in Room: {$room_name} on {$date}
cancel-booking-success = Booking has been cancelled