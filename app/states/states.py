from aiogram.fsm.state import StatesGroup, State


class Booking(StatesGroup):
    select_date = State()
    select_room = State()
    select_desk = State()


class CancelBookings(StatesGroup):
    select_booking = State()


class AllBookings(StatesGroup):
    select_room = State()
    view_bookings = State()