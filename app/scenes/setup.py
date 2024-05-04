from aiogram import F, Dispatcher
from aiogram.fsm.scene import SceneRegistry
from aiogram.filters import Command

from app.routers.admin.router import admin_router

from app.scenes.admin.main import AdminMenuScene


def register_scenes(dispatcher: Dispatcher):
    #* Create a SceneRegistry object
    scene_registry = SceneRegistry(dispatcher)
    
    #* Dynamically import and register all admin and user scenes
    from app.scenes.admin import __all__ as admin_scenes
    scene_registry.register(*admin_scenes)
    # from app.scenes.user import __all__ as user_scenes
    # scene_registry.register(*user_scenes)

    #* If you have scenes outside of the admin subpackage, import and register them similarly
    # from app.scenes.user import __all__ as user_scenes
    # scene_registry.register(*user_scenes)
    
    #* Register entry-point handlers for the scenes
    admin_router.message.register(AdminMenuScene.as_handler(), Command("admin"))
    # user_router.message.register(UserDateSelectScene.as_handler(), Command("book"))