import math

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from app.templating import templates

from app.dependencies import get_db
from app.functions.session_timeout import require_admin, require_comum, require_login
from app.models.compra import Compra

router = APIRouter()



@router.post("/compra/finalizar")
async def finalizar_compra(request: Request, db=Depends(get_db)):
    if not request.session.get("loggedin") or not request.session.get("idUsuario"):
        return JSONResponse({"success": False, "message": "Usuário não autenticado"})

    if request.session.get("idTipoLogin") != 1:
        return JSONResponse({"success": False, "message": "Apenas usuários comuns podem finalizar compras"})

    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"success": False, "message": "Dados inválidos"})

    itens = data.get("itens")
    if not itens:
        return JSONResponse({"success": False, "message": "Nenhum item no carrinho"})

    compra_model = Compra(db)
    resultado = compra_model.registrar_compra(request.session["idUsuario"], itens)
    return JSONResponse(resultado)


@router.get("/compras", response_class=HTMLResponse)
async def minhas_compras(request: Request, db=Depends(get_db)):
    require_login(request)
    if not request.session.get("idUsuario"):
        return RedirectResponse("/login", status_code=303)

    compra_model = Compra(db)
    compras = compra_model.listar_compras_usuario(request.session["idUsuario"])
    return templates.TemplateResponse(request,
        "compras/compras.html", {"request": request, "compras": compras})


@router.get("/compras/{id}", response_class=HTMLResponse)
async def detalhes_compra(request: Request, id: int, db=Depends(get_db)):
    require_login(request)
    if not request.session.get("idUsuario"):
        return RedirectResponse("/login", status_code=303)

    if id <= 0:
        return RedirectResponse("/compras?error=1", status_code=303)

    compra_model = Compra(db)
    compra = compra_model.get_compra_detalhes(id)

    if not compra or compra["idUsuario"] != request.session["idUsuario"]:
        return RedirectResponse("/compras?error=1", status_code=303)

    return templates.TemplateResponse(request,
        "compras/detalhes.html", {"request": request, "compra": compra})


@router.get("/vendas", response_class=HTMLResponse)
async def relatorio_vendas(request: Request, db=Depends(get_db)):
    require_admin(request)

    filtros = {
        "dataInicial": request.query_params.get("dataInicial", ""),
        "dataFinal": request.query_params.get("dataFinal", ""),
        "idUsuario": request.query_params.get("idUsuario", ""),
        "valorMinimo": request.query_params.get("valorMinimo", ""),
        "valorMaximo": request.query_params.get("valorMaximo", ""),
        "page": int(request.query_params.get("pagina", 1)),
        "itemsPerPage": 15,
    }

    compra_model = Compra(db)
    resultado = compra_model.listar_todas_compras(filtros)
    compras = resultado["compras"]
    estatisticas = resultado["estatisticas"]

    usuarios = compra_model.get_usuarios_com_compras()

    total_items = estatisticas["totalCompras"] or 0
    items_per_page = filtros["itemsPerPage"]
    pagina_atual = filtros["page"]
    total_paginas = math.ceil(total_items / items_per_page) if items_per_page else 0

    return templates.TemplateResponse(
        request,
        "vendas/relatorio.html",
        {
            "request": request,
            "filtros": filtros,
            "usuarios": usuarios,
            "compras": compras,
            "estatisticas": estatisticas,
            "paginaAtual": pagina_atual,
            "totalPaginas": total_paginas,
        },
    )


@router.get("/vendas/mensal", response_class=HTMLResponse)
async def relatorio_mensal(request: Request, db=Depends(get_db)):
    require_admin(request)

    try:
        ano = int(request.query_params.get("ano", 0)) or None
    except ValueError:
        ano = None

    compra_model = Compra(db)
    relatorio = compra_model.get_relatorio_mensal(ano)

    return templates.TemplateResponse(request,
        "vendas/relatorio-mensal.html", {"request": request, "relatorio": relatorio})


@router.get("/vendas/top-clientes", response_class=HTMLResponse)
async def top_clientes(request: Request, db=Depends(get_db)):
    require_admin(request)

    try:
        limit = int(request.query_params.get("limit", 10))
    except ValueError:
        limit = 10

    order_by = request.query_params.get("orderBy", "valorTotal")
    if order_by not in ("valorTotal", "totalCompras"):
        order_by = "valorTotal"

    periodo = request.query_params.get("periodo", "")
    if periodo not in ("mes", "trimestre", "semestre", "ano", ""):
        periodo = ""

    limit = max(1, min(50, limit))

    compra_model = Compra(db)
    resultado = compra_model.get_top_clientes(limit, order_by, periodo)

    return templates.TemplateResponse(request,
        "vendas/relatorio-clientes.html", {"request": request, "resultado": resultado})


@router.get("/vendas/canais", response_class=HTMLResponse)
async def relatorio_vendas_por_canal(request: Request, db=Depends(get_db)):
    require_admin(request)

    filtros = {
        "dataInicial": request.query_params.get("dataInicial", ""),
        "dataFinal": request.query_params.get("dataFinal", ""),
        "canal": request.query_params.get("canal", ""),
    }

    compra_model = Compra(db)
    resultado = compra_model.listar_vendas_por_canal(filtros)

    return templates.TemplateResponse(
        request,
        "vendas/relatorio-canais.html",
        {
            "request": request,
            "filtros": filtros,
            "vendasPorCanal": resultado["vendasPorCanal"],
            "totais": resultado["totais"],
            "canais": resultado["canais"],
        },
    )


@router.get("/vendas/{id}", response_class=HTMLResponse)
async def detalhes_venda_admin(request: Request, id: int, db=Depends(get_db)):
    require_admin(request)
    if id <= 0:
        return RedirectResponse("/vendas?error=1", status_code=303)

    compra_model = Compra(db)
    compra = compra_model.get_compra_detalhes(id)
    if not compra:
        return RedirectResponse("/vendas?error=1", status_code=303)

    return templates.TemplateResponse(
        request,
        "vendas/detalhes.html", {"request": request, "compra": compra},
    )
