from typing import AsyncGenerator
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config_data.config import load_config
from app.database.engine import get_engine, get_session_pool
from api.auth import get_auth_backend
from api.model_views import (
    UserAdmin,
    UserRoleAssignmentAdmin,
    TeamAdmin,
    TeamTreeAdmin,
    WaitlistAdmin,
    RoomAdmin,
    DeskAdmin,
    DeskAssignmentAdmin,
    BookingAdmin,
)


config = load_config()

engine = get_engine(db_url=config.db.url, echo=False)

session_pool = async_sessionmaker(engine, expire_on_commit=False)

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=config.sqladmin.secret_key)

templates = Jinja2Templates(directory=project_root / "api" / "templates")

auth_backend = get_auth_backend(secret_key=config.sqladmin.secret_key)

admin = Admin(app, engine, authentication_backend=auth_backend)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_pool() as session:
        yield session


admin.add_view(UserAdmin)
admin.add_view(UserRoleAssignmentAdmin)
admin.add_view(TeamAdmin)
admin.add_view(TeamTreeAdmin)
admin.add_view(WaitlistAdmin)
admin.add_view(RoomAdmin)
admin.add_view(DeskAdmin)
admin.add_view(DeskAssignmentAdmin)
admin.add_view(BookingAdmin)


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/")
async def login(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    success = await auth_backend.login(request)
    if success:
        return RedirectResponse(url="/admin", status_code=302)
    return templates.TemplateResponse("error.html", {"request": request, "message": "Invalid credentials"}, status_code=401)


@app.post("/logout")
async def logout(request: Request):
    await auth_backend.logout(request)
    return RedirectResponse(url="/")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.sqladmin.host,
        port=config.sqladmin.port,
        reload=True,
        log_level="info",
        lifespan="on",
    )
