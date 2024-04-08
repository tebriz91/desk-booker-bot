from typing import Literal

    
class TranslatorRunner:
    def get(self, path: str, **kwargs) -> str: ...
    
    button: Button
    select: Select
    selected: Selected
    existing: Existing
    desk: Desk
    there: There
    my: My
    no: No
    bookings: Bookings
    cancel: Cancel


class Button:
    cancel: ButtonCancel
    main: ButtonMain

    @staticmethod
    def yes() -> Literal["""Yes"""]: ...

    @staticmethod
    def no() -> Literal["""No"""]: ...

    @staticmethod
    def ok() -> Literal["""👌Ok"""]: ...

    @staticmethod
    def back() -> Literal["""⏪Back"""]: ...

    @staticmethod
    def next() -> Literal["""⏩Next"""]: ...

    @staticmethod
    def exit() -> Literal["""🏁Exit"""]: ...

    @staticmethod
    def confirm() -> Literal["""✅Confirm"""]: ...

    @staticmethod
    def toggle() -> Literal["""🔄Toggle"""]: ...


class ButtonCancel:
    all: ButtonCancelAll

    @staticmethod
    def __call__() -> Literal["""❌Cancel"""]: ...


class ButtonMain:
    @staticmethod
    def menu() -> Literal["""🏠Main Menu"""]: ...


class Select:
    booking: SelectBooking

    @staticmethod
    def date() -> Literal["""Select a date:"""]: ...

    @staticmethod
    def room() -> Literal["""Select a room:"""]: ...

    @staticmethod
    def desk() -> Literal["""Select a desk:"""]: ...


class Selected:
    @staticmethod
    def date(*, date) -> Literal["""Date: { $date }"""]: ...

    @staticmethod
    def room(*, room_name) -> Literal["""Room: { $room_name }"""]: ...


class Existing:
    @staticmethod
    def booking(*, date, room_name, desk_name) -> Literal["""You already have a booking on { $date } in room: { $room_name }, desk: { $desk_name }"""]: ...


class Desk:
    booker: DeskBooker

    @staticmethod
    def assignment(*, weekday) -> Literal["""You have an assigned desk for the selected weekday ({ $weekday })"""]: ...


class There:
    are: ThereAre


class ThereAre:
    no: ThereAreNo


class ThereAreNo:
    @staticmethod
    def desks(*, room_name, date) -> Literal["""For now there are no available desks in room: { $room_name } on: { $date }"""]: ...


class DeskBooker:
    @staticmethod
    def error() -> Literal["""Oops... Someone has booked the desk before you. Please select another desk"""]: ...

    @staticmethod
    def success(*, desk_name, room_name, date) -> Literal["""Successfully booked desk: { $desk_name } in room: { $room_name } for { $date }"""]: ...


class My:
    bookings: MyBookings


class MyBookings:
    no: MyBookingsNo

    @staticmethod
    def greeting(*, telegram_name) -> Literal["""Your bookings, { $telegram_name }:"""]: ...

    @staticmethod
    def date(*, date) -> Literal["""&lt;b&gt;{ $date }&lt;/b&gt;"""]: ...

    @staticmethod
    def desk(*, room_name, desk_name) -> Literal["""Room: { $room_name }, Desk: { $desk_name }"""]: ...

    @staticmethod
    def bookedOn(*, booked_on) -> Literal["""&lt;code&gt;booked on: { $booked_on }&lt;/code&gt;"""]: ...

    @staticmethod
    def list(*, date, room_name, desk_name, booked_on) -> Literal["""&lt;b&gt;{ $date }&lt;/b&gt;
    Room: { $room_name }, Desk: { $desk_name }
    &lt;code&gt;booked on: { $booked_on }&lt;/code&gt;"""]: ...


class MyBookingsNo:
    @staticmethod
    def bookings() -> Literal["""You have no bookings yet"""]: ...


class No:
    bookings: NoBookings


class NoBookings:
    to: NoBookingsTo


class NoBookingsTo:
    @staticmethod
    def cancel() -> Literal["""You have no bookings to cancel"""]: ...


class SelectBooking:
    to: SelectBookingTo


class SelectBookingTo:
    @staticmethod
    def cancel() -> Literal["""Select a booking to cancel:"""]: ...


class Bookings:
    to: BookingsTo


class BookingsTo:
    @staticmethod
    def cancel(*, desk_name, room_name, date) -> Literal["""Desk: { $desk_name } in Room: { $room_name } on { $date }"""]: ...


class Cancel:
    booking: CancelBooking


class CancelBooking:
    @staticmethod
    def success() -> Literal["""Booking has been cancelled"""]: ...


class ButtonCancelAll:
    @staticmethod
    def bookings() -> Literal["""❌Cancel all bookings"""]: ...

