# from typing import Any

# from aiogram import F
# from aiogram.filters import Command
# from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton

# from aiogram.utils.keyboard import ReplyKeyboardBuilder

# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.scene import Scene, on

# from keyboards.admin_kb import create_admin_kb

# from enums.admin_kb_buttons import AdminKB


# class AdminPanelScene(Scene, state="admin_panel"):
#     """
#     This class represents the admin panel scene.
#     It inherits from the Scene class and has a state of "admin_panel".
#     It is registered in the admin_router.
#     """
    
#     @on.message.enter()
#     async def on_enter(self, message: Message, state: FSMContext, step: int | None = 0) -> Any:
#         """
#         This method is called when the admin enters the admin panel scene.
        
#         It displays the admin panel reply keyboard.
        
#         :param message: The message object.
#         :param step: Scene argument, can be passed to the scene using the wizard
#         :return:
#         """ 
#         if not step:
#             # This is the first step of the scene
            
#             keyboard = ReplyKeyboardBuilder()
#             keyboard.button(text=AdminKB.USER_MANAGEMENT.value)
#             keyboard.button(text=AdminKB.ROOM_MANAGEMENT.value)
#             keyboard.button(text=AdminKB.BOOKING_MANAGEMENT.value)
#             keyboard.button(text=AdminKB.ANALYTICS.value)     
#             keyboard.button(text="Back")
#             keyboard.button(text="Exit")
            
#             await message.answer("Welcome to the admin panel", reply_markup=keyboard.adjust(2).as_markup(resize_keyboard=True))
#         else:
#             # This is the second step of the scene
#             await message.answer("You are in the admin panel")
        
#     @on.message.exit()
#     async def on_exit(self, message: Message, state: FSMContext) -> None:
#         """
#         This method is called when the admin exits the admin panel scene.
        
#         It displays a message to the admin.
        
#         :param message: The message object.
#         :return:
#         """
#         # Answer the user and remove keyboard
#         await message.answer(
#             text="You have exited the admin panel",
#             reply_markup=ReplyKeyboardRemove())
#         await self.wizard.exit()
    
#     @on.message(F.text == 'User Management')
#     async def enter_user_management(self, message: Message, state: FSMContext):
        
#         keyboard = ReplyKeyboardBuilder()
#         keyboard.button(text="Add User")
#         keyboard.button(text="Remove User")     
#         keyboard.button(text="Back")
#         keyboard.button(text="Exit")
        
#         await message.answer(
#             text="You have entered the user management panel",
#             reply_markup=keyboard.adjust(2).as_markup(resize_keyboard=True))
        
#     # @on.message.back()