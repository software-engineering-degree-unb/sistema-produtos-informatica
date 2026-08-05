import bcrypt
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templating import templates

from app.dependencies import get_db
from app.functions.historico import registrar_operacao
from app.models.login import User

router = APIRouter()



@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request,
        "auth/login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, db=Depends(get_db)):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    if username is not None and password is not None:
        user_model = User(db)
        row = user_model.authenticate(username)

        if row is None:
            registrar_operacao(db, None, "LOGIN", "FALHA", "Falha na consulta de autenticação", request)
            return RedirectResponse("/login?error=4", status_code=303)

        try:
            senha_valida = bcrypt.checkpw(password.encode("utf-8"), row["senha"].encode("utf-8"))
        except ValueError:
            senha_valida = False

        if senha_valida:
            if row["idSituacaoUsuario"] == 1:
                request.session["loggedin"] = True
                request.session["login"] = row["login"]
                request.session["id"] = row["idLogin"]
                request.session["idTipoLogin"] = row["idTipoLogin"]
                request.session["nome"] = row["nome"]
                request.session["idUsuario"] = row["idUsuario"]
                registrar_operacao(db, row["idLogin"], "LOGIN", "SUCESSO", None, request)
                return RedirectResponse("/?success=1", status_code=303)
            else:
                registrar_operacao(db, row["idLogin"], "LOGIN", "FALHA", "Usuario inativo", request)
                return RedirectResponse("/login?error=1", status_code=303)
        else:
            registrar_operacao(db, row["idLogin"], "LOGIN", "FALHA", "Senha incorreta", request)
            return RedirectResponse("/login?error=2", status_code=303)
    else:
        registrar_operacao(db, None, "LOGIN", "FALHA", "Dados de login incompletos", request)
        return RedirectResponse("/login?error=5", status_code=303)

    return templates.TemplateResponse(request,
        "auth/login.html", {"request": request})


@router.get("/logout")
async def logout(request: Request, db=Depends(get_db)):
    id_login = request.session.get("id")
    if id_login:
        registrar_operacao(db, id_login, "LOGOUT", "SUCESSO", None, request)
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
