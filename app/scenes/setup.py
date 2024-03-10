from aiogram import Dispatcher
from aiogram.fsm.scene import SceneRegistry
from aiogram.filters import Command

from routers.admin.router import admin_router

from scenes.admin.main import AdminMenuScene

def register_scenes(dispatcher: Dispatcher):
    # Create a SceneRegistry object
    scene_registry = SceneRegistry(dispatcher)
    
    # Dynamically import and register all admin scenes
    from scenes.admin import __all__ as admin_scenes
    scene_registry.register(*admin_scenes)

    # If you have scenes outside of the admin subpackage, import and register them similarly
    # from scenes.user import __all__ as user_scenes
    # scene_registry.register(*user_scenes)
    
    # Register entry-point handlers for the scenes
    admin_router.message.register(AdminMenuScene.as_handler(), Command("admin"))