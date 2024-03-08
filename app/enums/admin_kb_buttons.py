from enum import Enum

class AdminKB(Enum):
    USER_MANAGEMENT = 'User Management'
    ROOM_MANAGEMENT = 'Room Management'
    BOOKING_MANAGEMENT = 'Booking Management'
    ANALYTICS = 'Analytics'
    
    def __str__(self):
        return self.value