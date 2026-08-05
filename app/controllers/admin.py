from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templating import templates

from app.dependencies import get_db
from app.functions.session_timeout import require_admin
from app.models.admin import Admin
from app.models.usuario import Usuario

router = APIRouter()



@router.get("/usuarios", response_class=HTMLResponse)
async def list_usuarios(request: Request, db=Depends(get_db)):
    require_admin(request)

    search_term = request.query_params.get("search", "")
    search_type = request.query_params.get("searchType", "nome")
    status = request.query_params.get("status", "todos")

    admin_model = Admin(db)
    usuario_model = Usuario(db)

    usuario_details = usuario_model.get_by_id(request.session["id"])
    admin_details = admin_model.get_by_id(request.session["id"])

    if search_term or status != "todos":
        usuarios = admin_model.search_usuarios(search_type, search_term, status)
    else:
        usuarios = admin_model.get_all_usuarios()

    return templates.TemplateResponse(
        request,
        "usuarios/list.html",
        {
            "request": request,
            "usuarios": usuarios,
            "usuario": usuario_details,
            "admin": admin_details,
            "search": search_term,
            "searchType": search_type,
            "status": status,
        },
    )


@router.get("/usuarios/novo", response_class=HTMLResponse)
async def create_usuario_page(request: Request, db=Depends(get_db)):
    require_admin(request)
    admin_model = Admin(db)
    usuario_model = Usuario(db)
    usuario_details = usuario_model.get_by_id(request.session["id"])
    admin_details = admin_model.get_by_id(request.session["id"])
    return templates.TemplateResponse(
        request,
        "usuarios/create.html",
        {"request": request, "usuario": usuario_details, "admin": admin_details},
    )


@router.post("/usuarios/novo", response_class=HTMLResponse)
async def create_usuario(request: Request, db=Depends(get_db)):
    require_admin(request)
    form = await request.form()
    data = {
        "nome": form.get("nome", ""),
        "documento": form.get("documento", ""),
        "login": form.get("login", ""),
        "senha": form.get("senha", ""),
        "tipoLogin": form.get("tipoLogin", ""),
        "cep": form.get("cep", ""),
        "uf": form.get("uf", ""),
        "municipio": form.get("municipio", ""),
        "rua": form.get("rua", ""),
        "numero": form.get("numero", ""),
        "complemento": form.get("complemento", "") or "",
    }

    admin_model = Admin(db)
    if admin_model.create_usuario(data, request.session.get("id")):
        return RedirectResponse("/usuarios?success=1", status_code=303)
    return RedirectResponse("/usuarios/novo?error=1", status_code=303)


@router.get("/usuarios/{id}/editar", response_class=HTMLResponse)
async def edit_usuario_page(request: Request, id: int, db=Depends(get_db)):
    require_admin(request)
    admin_model = Admin(db)
    usuario_model = Usuario(db)
    usuario_details = usuario_model.get_by_id(request.session["id"])
    admin_details = admin_model.get_by_id(request.session["id"])
    usuario = admin_model.get_usuario_by_id(id)
    if not usuario:
        return RedirectResponse("/usuarios?error=Usuário não encontrado", status_code=303)
    return templates.TemplateResponse(
        request,
        "usuarios/edit.html",
        {
            "request": request,
            "usuario": usuario,
            "usuario_details": usuario_details,
            "admin": admin_details,
        },
    )


@router.post("/usuarios/{id}/editar", response_class=HTMLResponse)
async def edit_usuario(request: Request, id: int, db=Depends(get_db)):
    require_admin(request)
    form = await request.form()
    data = {
        "nome": form.get("nome", ""),
        "documento": form.get("documento", ""),
        "login": form.get("login", ""),
        "senha": form.get("senha", ""),
        "tipoLogin": form.get("tipoLogin", ""),
        "status": form.get("status", ""),
        "cep": form.get("cep", ""),
        "uf": form.get("uf", ""),
        "municipio": form.get("municipio", ""),
        "rua": form.get("rua", ""),
        "numero": form.get("numero", ""),
        "complemento": form.get("complemento", "") or "",
    }

    admin_model = Admin(db)
    if admin_model.update_usuario(id, data, request.session.get("id")):
        return RedirectResponse("/usuarios?success=1", status_code=303)
    return RedirectResponse(f"/usuarios/{id}/editar?error=1", status_code=303)


@router.get("/historico/login", response_class=HTMLResponse)
async def historico_login(request: Request, db=Depends(get_db)):
    require_admin(request)

    data_final = date.today()
    data_inicial = date.today()

    if request.method == "POST":
        form = await request.form()
        data_inicial = form.get("data_inicial", data_inicial.isoformat())
        data_final = form.get("data_final", data_final.isoformat())
        tipo_operacao = form.get("tipo_operacao", "")
        status_operacao = form.get("status_operacao", "")
    else:
        data_inicial = data_inicial.isoformat()
        data_final = data_final.isoformat()
        tipo_operacao = ""
        status_operacao = ""

    if data_final < data_inicial:
        data_final = data_inicial

    admin_model = Admin(db)
    historico = _get_historico_login(db, data_inicial, data_final, tipo_operacao, status_operacao)

    filter_values = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "tipoOperacao": tipo_operacao,
        "statusOperacao": status_operacao,
    }

    return templates.TemplateResponse(
        request,
        "historico/login.html",
        {"request": request, "historico": historico, "filterValues": filter_values},
    )


@router.post("/historico/login", response_class=HTMLResponse)
async def historico_login_post(request: Request, db=Depends(get_db)):
    require_admin(request)

    form = await request.form()
    data_inicial = form.get("data_inicial", date.today().isoformat())
    data_final = form.get("data_final", date.today().isoformat())
    tipo_operacao = form.get("tipo_operacao", "")
    status_operacao = form.get("status_operacao", "")

    if data_final < data_inicial:
        data_final = data_inicial

    historico = _get_historico_login(db, data_inicial, data_final, tipo_operacao, status_operacao)

    filter_values = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "tipoOperacao": tipo_operacao,
        "statusOperacao": status_operacao,
    }

    return templates.TemplateResponse(
        request,
        "historico/login.html",
        {"request": request, "historico": historico, "filterValues": filter_values},
    )


def _get_historico_login(db, data_inicial, data_final, tipo_operacao="", status_operacao=""):
    query = """
        SELECT
            h.dataOperacao,
            h.tipoOperacao,
            h.enderecoIP,
            h.userAgent,
            h.statusOperacao,
            h.detalhes,
            l.login AS login_usuario,
            u.nome AS nome_completo
        FROM historicoLogin h
        LEFT JOIN login l ON h.idLogin = l.idLogin
        LEFT JOIN usuario u ON l.idUsuario = u.idUsuario
        WHERE DATE(h.dataOperacao) >= %s
        AND DATE(h.dataOperacao) <= %s
    """
    params = [data_inicial, data_final]

    if tipo_operacao:
        query += " AND h.tipoOperacao = %s"
        params.append(tipo_operacao)

    if status_operacao:
        query += " AND h.statusOperacao = %s"
        params.append(status_operacao)

    query += " ORDER BY h.dataOperacao DESC"

    with db.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()


@router.get("/historico/alteracoes", response_class=HTMLResponse)
async def historico_alteracoes(request: Request, db=Depends(get_db)):
    require_admin(request)

    data_final = date.today()
    data_inicial = data_final - timedelta(days=31)

    data_inicial = data_inicial.isoformat()
    data_final = data_final.isoformat()
    tipo_operacao = ""

    admin_model = Admin(db)
    historico = admin_model.get_historico_alteracoes_usuario(data_inicial, data_final, tipo_operacao)

    filter_values = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "tipoOperacao": tipo_operacao,
    }

    return templates.TemplateResponse(
        request,
        "historico/alteracoes.html",
        {"request": request, "historico": historico, "filterValues": filter_values},
    )


@router.post("/historico/alteracoes", response_class=HTMLResponse)
async def historico_alteracoes_post(request: Request, db=Depends(get_db)):
    require_admin(request)

    form = await request.form()
    data_inicial = form.get("data_inicial", "")
    data_final = form.get("data_final", "")
    tipo_operacao = form.get("tipo_operacao", "")

    if not data_inicial:
        data_final = date.today()
        data_inicial = (data_final - timedelta(days=31)).isoformat()
        data_final = data_final.isoformat()

    diff = (datetime.strptime(data_final, "%Y-%m-%d") - datetime.strptime(data_inicial, "%Y-%m-%d")).days
    if diff < 0 or diff > 31:
        data_final = date.today()
        data_inicial = (data_final - timedelta(days=31)).isoformat()
        data_final = data_final.isoformat()

    admin_model = Admin(db)
    historico = admin_model.get_historico_alteracoes_usuario(data_inicial, data_final, tipo_operacao)

    filter_values = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "tipoOperacao": tipo_operacao,
    }

    return templates.TemplateResponse(
        request,
        "historico/alteracoes.html",
        {"request": request, "historico": historico, "filterValues": filter_values},
    )
