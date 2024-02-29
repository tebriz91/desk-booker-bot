from aiogram.fsm.state import State, StatesGroup

class FSMBooking(StatesGroup):
    select_date = State()
    select_room = State()
    select_desk = State()

class FSMAllBookings(StatesGroup):
    select_room = State()
    view_bookings = State()