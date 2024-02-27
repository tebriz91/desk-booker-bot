from aiogram import Router

from routers.admin import admin_router
from routers.user import user_router
# from routers.error import error_router
# from routers.other import other_router

router = Router(name='main')
router.include_routers(
    admin_router,
    user_router,
    # other_router,
    # error_router,
)