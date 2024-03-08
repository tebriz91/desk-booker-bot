from aiogram import Router

from filters.admin import AdminFilter

admin_router = Router(name='admin')
admin_router.message.filter(AdminFilter())