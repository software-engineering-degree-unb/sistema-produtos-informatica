import time

from fastapi import Request

from app.config.database import get_connection
from app.config.settings import SESSION_TIMEOUT
from app.functions.historico import registrar_operacao


class RedirectException(Exception):
    def __init__(self, url: str):
        self.url = url


def check_session_timeout(request: Request) -> None:
    last_activity = request.session.get("LAST_ACTIVITY")
    if last_activity is not None and (time.time() - last_activity) > SESSION_TIMEOUT:
        id_login = request.session.get("id")
        conn = get_connection()
        try:
            registrar_operacao(conn, id_login, "LOGOUT", "SUCESSO", "Tempo Expirado", request)
        finally:
            conn.close()
        request.session.clear()
        raise RedirectException("/login?timeout=1")
    request.session["LAST_ACTIVITY"] = time.time()


def require_login(request: Request) -> None:
    if not request.session.get("loggedin"):
        raise RedirectException("/login")
    check_session_timeout(request)


def require_admin(request: Request) -> None:
    if not request.session.get("loggedin"):
        raise RedirectException("/login")
    check_session_timeout(request)
    if request.session.get("idTipoLogin") != 2:
        raise RedirectException("/produtos?error=unauthorized")


def require_comum(request: Request) -> None:
    if not request.session.get("loggedin"):
        raise RedirectException("/login")
    check_session_timeout(request)
    if request.session.get("idTipoLogin") != 1:
        raise RedirectException("/")
