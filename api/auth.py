from typing import Union
from fastapi import Request
from fastapi.responses import RedirectResponse, Response
from sqladmin.authentication import AuthenticationBackend

from app.config_data.config import load_config


config = load_config()


class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str):
        super().__init__(secret_key)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        admin_username = config.sqladmin.login
        admin_password = config.sqladmin.password

        if username == admin_username and password == admin_password:
            request.session["user"] = {"username": username}
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Union[Response, bool]:
        user = request.session.get("user")
        if user:
            return True
        return RedirectResponse(url="/")


def get_auth_backend(secret_key: str) -> AdminAuth:
    return AdminAuth(secret_key=secret_key)
