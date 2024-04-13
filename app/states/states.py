from aiogram.fsm.state import StatesGroup, State


class Booking(StatesGroup):
    select_date = State()
    select_room = State()
    select_desk = State()


class CancelBookings(StatesGroup):
    select_booking = State()


class TeamBookings(StatesGroup):
    select_team = State()
    select_subteam = State()
    view_bookings = State()


class AllBookings(StatesGroup):
    select_room = State()
    view_bookings = State()


class Team(StatesGroup):
    main_menu = State()
    bookings = State()


class Desk(StatesGroup):
    main_menu = State()