from enum import Enum

class ButtonLabel(Enum):
    CANCEL = '❌Cancel'
    EXIT = '🏁Exit'
    BACK = '⏪Back'
    NEXT = '⏩Next'
    TO_MAIN_MENU = '↩️Main Menu'
    OK = '🆗'
    YES = 'Yes'
    NO = 'No'
    CONFIRM = '✅Confirm'
    
    def __str__(self):
        return self.value