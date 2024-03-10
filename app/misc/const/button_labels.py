from enum import Enum

class ButtonLabel(Enum):
    CANCEL = 'Cancel'
    EXIT = 'Exit'
    OK = 'Ok'
    BACK = 'Back'
    NEXT = 'Next'

    def __str__(self):
        return self.value