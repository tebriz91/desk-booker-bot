from typing import Literal

    
class TranslatorRunner:
    def get(self, path: str, **kwargs) -> str: ...
    
    button: Button
    select: Select
    selected: Selected
    no: No
    existing: Existing
    desk: Desk
    there: There
    my: My
    bookings: Bookings
    cancel: Cancel
    all: All
    team: Team


class Button:
    main: ButtonMain

    @staticmethod
    def yes() -> Literal["""Yes"""]: ...

    @staticmethod
    def no() -> Literal["""No"""]: ...

    @staticmethod
    def ok() -> Literal["""👌Ok"""]: ...

    @staticmethod
    def cancel() -> Literal["""❌Cancel"""]: ...

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

    @staticmethod
    def desk(*, desk_name) -> Literal["""Desk: { $desk_name }"""]: ...


class No:
    bookings: NoBookings

    @staticmethod
    def rooms() -> Literal["""There are no rooms yet"""]: ...


class Existing:
    @staticmethod
    def booking(*, date, room_name, desk_name) -> Literal["""You already have a 🚩booking on { $date } in room: { $room_name }, desk: { $desk_name }"""]: ...


class Desk:
    assignment: DeskAssignment
    booker: DeskBooker


class DeskAssignment:
    @staticmethod
    def __call__(*, weekday) -> Literal["""You have an 🔒assigned desk for the selected weekday ({ $weekday }). To see your permanent desk assinments use command: /desk"""]: ...

    @staticmethod
    def empty() -> Literal["""You don&#39;t have an 🔒assigned desk"""]: ...

    @staticmethod
    def greeting() -> Literal["""Your 🔒desk assignment(s):"""]: ...

    @staticmethod
    def info(*, weekday, room_name, desk_name) -> Literal["""&lt;b&gt;{ $weekday }&lt;/b&gt;
    Room: &lt;b&gt;{ $room_name }&lt;/b&gt;, Desk: &lt;b&gt;{ $desk_name }&lt;/b&gt;"""]: ...

    @staticmethod
    def active() -> Literal["""Desk assignment(s) is ✅active

In case you are out of the office (vacation, sick leave, etc.), please press the button below to free the desk(s) until your return"""]: ...

    @staticmethod
    def inactive() -> Literal["""Desk assignment(s) is ❌inactive

In case you are back to the office, press the button below to activate desk assignment(s)"""]: ...


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
    def success(*, desk_name, room_name, date) -> Literal["""Successfully 🚩booked desk: { $desk_name } in room: { $room_name } for { $date }"""]: ...


class My:
    bookings: MyBookings


class MyBookings:
    no: MyBookingsNo

    @staticmethod
    def greeting(*, telegram_name) -> Literal["""Your 🚩bookings, { $telegram_name }:"""]: ...

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
    def bookings() -> Literal["""You have no 🚩bookings yet"""]: ...


class NoBookings:
    to: NoBookingsTo


class NoBookingsTo:
    @staticmethod
    def cancel() -> Literal["""You have no 🚩bookings to cancel"""]: ...


class SelectBooking:
    to: SelectBookingTo


class SelectBookingTo:
    @staticmethod
    def cancel() -> Literal["""Select a 🚩booking to cancel:"""]: ...


class Bookings:
    to: BookingsTo


class BookingsTo:
    @staticmethod
    def cancel(*, date, desk_name, room_name) -> Literal["""{ $date }, Desk: { $desk_name }, Room: { $room_name }"""]: ...


class Cancel:
    booking: CancelBooking


class CancelBooking:
    @staticmethod
    def success() -> Literal["""Booking has been cancelled"""]: ...


class All:
    bookings: AllBookings


class AllBookings:
    no: AllBookingsNo
    desk: AllBookingsDesk

    @staticmethod
    def greeting(*, room_name) -> Literal["""&lt;b&gt;🚩Bookings in Room: { $room_name }&lt;/b&gt;"""]: ...

    @staticmethod
    def date(*, date) -> Literal["""&lt;b&gt;{ $date }&lt;/b&gt;"""]: ...


class AllBookingsNo:
    bookings: AllBookingsNoBookings


class AllBookingsNoBookings:
    @staticmethod
    def __call__() -> Literal["""There are no 🚩bookings in this room yet"""]: ...

    @staticmethod
    def assignments() -> Literal["""There are no 🚩bookings and 🔒permanent desk assignments in this room yet"""]: ...


class AllBookingsDesk:
    assignments: AllBookingsDeskAssignments

    @staticmethod
    def user(*, desk_name, telegram_name) -> Literal["""Desk: { $desk_name }, { $telegram_name }"""]: ...


class AllBookingsDeskAssignments:
    first: AllBookingsDeskAssignmentsFirst

    @staticmethod
    def weekday(*, weekday) -> Literal["""{ $weekday }"""]: ...


class AllBookingsDeskAssignmentsFirst:
    @staticmethod
    def line(*, room_name) -> Literal["""&lt;b&gt;Active 🔒permanent desk assignments in Room: { $room_name }&lt;/b&gt;"""]: ...


class Team:
    no: TeamNo
    room: TeamRoom
    member: TeamMember

    @staticmethod
    def empty() -> Literal["""Your team is not defined yet"""]: ...

    @staticmethod
    def name(*, team_name) -> Literal["""Team: { $team_name }"""]: ...


class TeamNo:
    @staticmethod
    def info() -> Literal["""There is no information about your team yet"""]: ...


class TeamRoom:
    @staticmethod
    def name(*, room_name) -> Literal["""Room: { $room_name }"""]: ...


class TeamMember:
    @staticmethod
    def info(*, telegram_name, role) -> Literal["""{ $telegram_name }, role: { $role }"""]: ...

