from enum import Enum

class MainMenu(Enum):
    BOOK = ('/book', 'Book a Desk')
    CANCEL_BOOKINGS = ('/cancel', 'Cancel Booking')
    MY_BOOKINGS = ('/my_bookings', 'View My Bookings')
    ALL_BOOKINGS = ('/all_bookings', 'View All Bookings')
    HELP = ('/help', 'Help Information')
    ADMIN = ('/admin', 'Admin Commands')
    
    def __str__(self):
        return self.value[0]  # Command
    
    @property
    def description(self):
        return self.value[1]  # Description