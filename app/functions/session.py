from fastapi import Request


def is_logged_in(request: Request) -> bool:
    return bool(request.session.get("loggedin"))


def is_admin(request: Request) -> bool:
    return request.session.get("idTipoLogin") == 2


def is_comum(request: Request) -> bool:
    return request.session.get("idTipoLogin") == 1
