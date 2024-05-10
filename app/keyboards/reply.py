from typing import List, Optional

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_reply_keyboard(
    buttons: Optional[List[str]] = None,
    width: int = 2,
    util_buttons: Optional[List[str]] = None,
    width_util: int = 2,
    one_time_keyboard: Optional[bool] = None,
    input_field_placeholder: Optional[str] = None,
    ) -> ReplyKeyboardMarkup:
    
    """
    Create a reply keyboard with main and utility buttons.
    This function takes a list of main buttons and a list of utility buttons, checks if they are not None, and creates a reply keyboard with the main and utility buttons.
    
    :param buttons: A list of main buttons.
    :param width: The width of the main buttons.
    :param util_buttons: A list of utility buttons.
    :param width_util: The width of the utility buttons.
    :return: A reply keyboard with main and utility buttons. Or only main buttons. Or only utility buttons.
    """
    
    main_keyboard = ReplyKeyboardBuilder()
    util_keyboard = ReplyKeyboardBuilder()

    # Add main buttons and adjust their layout
    if buttons:
        for button in buttons:
            main_keyboard.add(KeyboardButton(text=button))
        main_keyboard.adjust(width)
    
    # Add utility buttons and adjust their layout
    if util_buttons:
        for button in util_buttons:
            util_keyboard.add(KeyboardButton(text=button))
        util_keyboard.adjust(width_util)
    
    # Merge the main and utility keyboards
    combined_markup = main_keyboard.export() + util_keyboard.export()
    # Create the final keyboard markup from the combined layout
    final_keyboard = ReplyKeyboardMarkup(
        keyboard = combined_markup,
        resize_keyboard = True,
        one_time_keyboard = one_time_keyboard if one_time_keyboard else None,
        input_field_placeholder = input_field_placeholder if input_field_placeholder else None)
    
    return final_keyboard