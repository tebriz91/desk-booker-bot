from enum import Enum


class MainMenu(Enum):
    BOOK = ('/book', 'Book a Desk')
    CANCEL_BOOKINGS = ('/cancel', 'Cancel Booking')
    MY_BOOKINGS = ('/my_bookings', 'My Bookings')
    # TEAM_BOOKINGS = ('/team_bookings', 'Team Bookings')
    ALL_BOOKINGS = ('/all_bookings', 'All Bookings')
    TEAM = ('/team', 'My Team')
    DESK = ('/desk', 'My Desk')
    ADMIN = ('/admin', 'Admin Commands')

    
    def __str__(self):
        return self.value[0]  # Command

    
    @property
    def description(self):
        return self.value[1]  # Description