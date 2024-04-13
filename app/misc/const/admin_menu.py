from enum import Enum

#* Admin Menu
class AdminMenu(Enum):
    USER_MANAGEMENT = 'User Management'
    WAITLIST = 'Waitlist'
    ROOM_MANAGEMENT = 'Room Management'
    BOOKING_MANAGEMENT = 'Booking Management'
    ANALYTICS = 'Analytics'
    
    def __str__(self):
        return self.value

#* Submenus for Admin Menu
class UserManagementMenu(Enum):
    ADD_USER = 'Add User'
    DELETE_USER = 'Delete User'
    EDIT_USER = 'Edit User'
    BAN_USER = 'Ban User'
    UNBAN_USER = 'Unban User'
    BROWSE_USERS = 'Browse Users' # TODO: Add browse users logic

    def __str__(self):
        return self.value

class RoomManagementMenu(Enum):
    ADD_ROOM = 'Add Room'
    DELETE_ROOM = 'Delete Room'
    EDIT_ROOM = 'Edit Room'
    BROWSE_ROOMS = 'Browse Rooms'

    def __str__(self):
        return self.value

class BookingManagementMenu(Enum):
    BROWSE_BOOKINGS = 'Browse Bookings'
    CANCEL_BOOKINGS = 'Cancel Bookings'
    
    def __str__(self):
        return self.value

class AnalyticsMenu(Enum):
    USER_ANALYTICS = 'User Analytics'
    ROOM_ANALYTICS = 'Room Analytics'
    DESK_ANALYTICS = 'Desk Analytics'
    BOOKING_ANALYTICS = 'Booking Analytics'

    def __str__(self):
        return self.value

#* Submenus for User Management Menu (submenu of Admin Menu)
class UserDeleteMenu(Enum):
    SELECT_USER = 'Select User'
    DELETE_BY_ID = 'Delete by ID'
    DELETE_BY_USERNAME = 'Delete by Username'

    def __str__(self):
        return self.value

class UserEditMenu(Enum):
    SELECT_USER = 'Select User'
    EDIT_BY_ID = 'Edit by ID'
    EDIT_BY_USERNAME = 'Edit by Username'
    
    def __str__(self):
        return self.value
    
class UserBanMenu(Enum):
    ... # TODO: Add buttons for user ban menu

class UserUnbanMenu(Enum):
    ... # TODO: Add buttons for user unban menu

#* Submenus for Room Management Menu (submenu of Admin Menu)
class RoomDeleteMenu(Enum):
    SELECT_ROOM = 'Select Room'
    DELETE_BY_ID = 'Delete by ID'
    DELETE_BY_NAME = 'Delete by Name'

    def __str__(self):
        return self.value
    
class RoomEditMenu(Enum):
    EDIT_ROOM_NAME = 'Edit Name'
    TOGGLE_AVAILABILITY = 'Toggle Availability'
    EDIT_ROOM_PLAN = 'Edit Room Plan'
    ADD_DESK = 'Add Desk'
    DELETE_DESK = 'Delete Desk'
    EDIT_DESK = 'Edit Desk'
    
    def __str__(self):
        return self.value

#* Submenus for Room Edit Menu (submenu of Room Management Menu)
class DeskEditMenu(Enum):
    EDIT_DESK_NAME = 'Edit Desk Name'
    TOGGLE_AVAILABILITY = 'Toggle Availability'

#* Submenus for Booking Management Menu (submenu of Admin Menu)
class BookingBrowseMenu(Enum):
    BROWSE_PAST_BOOKINGS = 'Browse Past Bookings'
    BROWSE_CURRENT_BOOKINGS = 'Browse Current Bookings'
    BROWSE_BY_USER = 'Browse by User'
    BROWSE_BY_ROOM = 'Browse by Room'
    BROWSE_BY_DESK = 'Browse by Desk'

    def __str__(self):
        return self.value

class BookingCancelMenu(Enum):
    SELECT_DATE = 'Select Date'
    SELECT_ROOM = 'Select Room'
    SELECT_DESK = 'Select Desk'
    SELECT_USER = 'Select User'

    def __str__(self):
        return self.value
    
#* Submenus for Analytics Menu (submenu of Admin Menu)
# TODO: Add submenus for Analytics Menu