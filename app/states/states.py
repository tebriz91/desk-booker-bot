from aiogram.fsm.state import StatesGroup, State


class Booking(StatesGroup):
    select_date = State()
    select_room = State()
    select_desk = State()


class AllBookings(StatesGroup):
    select_room = State()
    view_bookings = State()


class CancelBooking(StatesGroup):
    select_booking = State()
    view_bookings = State()