from aiogram import Router

from app.filters.admin import AdminFilter


admin_router = Router(name='admin')
admin_router.message.filter(AdminFilter())
admin_router.callback_query.filter(AdminFilter())