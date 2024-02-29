from enum import Enum

class ButtonLabel(Enum):
    CANCEL = 'Cancel'
    BACK = 'Back'
    NEXT = 'Next'

    def __str__(self):
        return self.value