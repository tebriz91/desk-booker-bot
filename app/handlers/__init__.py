'''
from aiogram import Router

from app.routers.admin import admin_router
from app.routers.user import user_router
from app.routers.error import error_router
# from app.routers.other import other_router

router = Router(name='main')
router.include_routers(
    admin_router,
    user_router,
    # other_router,
    error_router,
)
'''