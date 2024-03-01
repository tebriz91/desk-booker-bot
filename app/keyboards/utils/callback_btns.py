from typing import Optional, List, Dict, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.callbacks import CBFUtilButtons

#* Generate an inline keyboard with util buttons based on provided parameters
def get_inline_keyboard_with_util_buttons(
    *,
    button_order: List[str],
    sizes: Tuple[int] = (2,),
    back_btn: Optional[str] = None,
    next_btn: Optional[str] = None,
    cancel_btn: Optional[str] = None,
    exit_btn: Optional[str] = None,
    ok_btn: Optional[str] = None
    ) -> InlineKeyboardMarkup:
    """
    Generate an inline keyboard with util buttons based on provided parameters, allowing customization of the number of utility buttons per row and their order.
    
    :param button_order: A list of button identifiers in the desired order.
    :param sizes: Width for each row of buttons.
    :param back_btn: Text for the "Back" button. None if not needed.
    :param next_btn: Text for the "Next" button. None if not needed.
    :param cancel_btn: Text for the "Cancel" button. None if not needed.
    :param exit_btn: Text for the "Exit" button. None if not needed.
    :param ok_btn: Text for the "Ok" button. None if not needed.
    :return: An instance of InlineKeyboardMarkup.
    """
    keyboard = InlineKeyboardBuilder()

    btns = {
        'back': back_btn, # identifier: button text
        'next': next_btn,
        'cancel': cancel_btn,
        'exit': exit_btn,
        'ok': ok_btn}

    # Add buttons to the builder based on the specified order
    for identifier in button_order:
        button_text = btns.get(identifier)
        if button_text:
            # Generate callback_data using the button's text/value
            callback_data = CBFUtilButtons(action=button_text).pack()
            keyboard.add(InlineKeyboardButton(
                text=button_text, 
                callback_data=callback_data
            ))

    # Adjust the buttons into rows according to the specified sizes
    keyboard.adjust(*sizes, repeat=True)  # repeat=True to cycle sizes if needed
    
    return keyboard.adjust(*sizes).as_markup()

def get_callback_util_btns(
    *,
    util_buttons_order: List[str],
    back_btn: Optional[str] = None,
    next_btn: Optional[str] = None,
    cancel_btn: Optional[str] = None,
    exit_btn: Optional[str] = None,
    ok_btn: Optional[str] = None
) -> List[Tuple[str, str]]:
    """
    Generate a list of utility buttons based on provided parameters and their desired order,
    so it can be used in functions like create_kb_with_dates to add util buttons to the keyboard.
    
    :param button_order: A list of button identifiers indicating the order of the buttons.
    :param back_btn: Text for the "Back" button. None if not needed.
    :param next_btn: Text for the "Next" button. None if not needed.
    :param cancel_btn: Text for the "Cancel" button. None if not needed.
    :param exit_btn: Text for the "Exit" button. None if not needed.
    :param ok_btn: Text for the "Ok" button. None if not needed.
    :return: A list of tuples, where each tuple contains the button text and its callback data.
    """
    # Mapping of button identifiers to their text and callback data packer
    btns = {
        'back': (back_btn, lambda: CBFUtilButtons(action=back_btn).pack()),
        'next': (next_btn, lambda: CBFUtilButtons(action=next_btn).pack()),
        'cancel': (cancel_btn, lambda: CBFUtilButtons(action=cancel_btn).pack()),
        'exit': (exit_btn, lambda: CBFUtilButtons(action=exit_btn).pack()),
        'ok': (ok_btn, lambda: CBFUtilButtons(action=ok_btn).pack()),
    }

    # Generate the ordered list of utility buttons based on button_order
    ordered_util_btns = [
        (text, packer()) 
        for identifier in util_buttons_order 
        if (text := btns.get(identifier)[0]) is not None and (packer := btns.get(identifier)[1]) is not None
    ]

    return ordered_util_btns










'''
#* Generate an inline keyboard with util buttons based on provided parameters
def get_inline_keyboard_with_util_buttons(
    *,
    sizes: tuple[int] = (2,),
    back_btn: Optional[str] = None,
    next_btn: Optional[str] = None,
    cancel_btn: Optional[str] = None,
    exit_btn: Optional[str] = None,
    ok_btn: Optional[str] = None
    ) -> InlineKeyboardMarkup:
    """
    Generate an inline keyboard with util buttons based on provided parameters.
    
    :param sizes: Width for each row of buttons.
    :param back_btn: Text for the "Back" button. None if not needed.
    :param next_btn: Text for the "Next" button. None if not needed.
    :param cancel_btn: Text for the "Cancel" button. None if not needed.
    :param exit_btn: Text for the "Exit" button. None if not needed.
    :param ok_btn: Text for the "OK" button. None if not needed.
    :return: An instance of InlineKeyboardMarkup.
    """
    keyboard = InlineKeyboardBuilder()

    if back_btn:
        keyboard.add(InlineKeyboardButton(
            text=back_btn,
            callback_data=CBFUtilButtons(action=back_btn).pack()
        ))
    if next_btn:
        keyboard.add(InlineKeyboardButton(
            text=next_btn,
            callback_data=CBFUtilButtons(action=next_btn).pack()
        ))
    if cancel_btn:
        keyboard.add(InlineKeyboardButton(
            text=cancel_btn,
            callback_data=CBFUtilButtons(action=cancel_btn).pack()
        ))
    if exit_btn:
        keyboard.add(InlineKeyboardButton(
            text=exit_btn,
            callback_data=CBFUtilButtons(action=exit_btn).pack()
        ))
    if ok_btn:
        keyboard.add(InlineKeyboardButton(
            text=ok_btn,
            callback_data=CBFUtilButtons(action=ok_btn).pack()
        ))

    return keyboard.adjust(*sizes).as_markup()
'''