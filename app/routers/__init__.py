from aiogram import Router

from .admin import admin_router
from .user import user_router
# from .error import error_router
# from .other import other_router

router = Router(name='main')
router.include_routers(
    admin_router,
    user_router,
    # other_router,
    # error_router,
)