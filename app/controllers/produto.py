import base64

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from app.templating import templates

from app.dependencies import get_db
from app.functions.session_timeout import require_admin, require_login
from app.models.produto import Produto

router = APIRouter()



@router.get("/produtos", response_class=HTMLResponse)
async def list_produtos(request: Request, db=Depends(get_db)):
    require_login(request)

    search_term = request.query_params.get("search", "")
    tipo_produto = request.query_params.get("tipoProduto") or None
    try:
        page = int(request.query_params.get("pagina", 1))
    except ValueError:
        page = 1

    visibilidade = (
        1
        if request.session["idTipoLogin"] == 1
        else (request.query_params.get("visibilidade") or None)
    )

    produto_model = Produto(db)
    result = produto_model.search_produtos(search_term, "geral", tipo_produto, visibilidade, page, 10)

    produtos = result["produtos"]
    total_items = result["totalItems"]
    items_per_page = result["itemsPerPage"]
    pagina_atual = result["currentPage"]

    import math

    total_paginas = math.ceil(total_items / items_per_page) if items_per_page else 0

    tipos_produto = produto_model.get_tipos_produto()
    visibilidade_produto = produto_model.get_visibilidade_produto()

    return templates.TemplateResponse(
        request,
        "produtos/list.html",
        {
            "request": request,
            "produtos": produtos,
            "tiposProduto": tipos_produto,
            "visibilidadeProduto": visibilidade_produto,
            "totalPaginas": total_paginas,
            "paginaAtual": pagina_atual,
            "search": search_term,
            "tipoProdutoSelecionado": request.query_params.get("tipoProduto", ""),
            "visibilidadeSelecionado": request.query_params.get("visibilidade", ""),
        },
    )


@router.get("/produtos/novo", response_class=HTMLResponse)
async def create_produto_page(request: Request, db=Depends(get_db)):
    require_admin(request)
    produto_model = Produto(db)
    tipos_produto = produto_model.get_tipos_produto()
    return templates.TemplateResponse(
        request,
        "produtos/create.html", {"request": request, "tiposProduto": tipos_produto}
    )


@router.post("/produtos/novo")
async def create_produto(request: Request, db=Depends(get_db)):
    require_admin(request)
    try:
        form = await request.form()

        imagens = []
        for key, value in form.multi_items():
            if key.startswith("imagens["):
                if hasattr(value, "read"):
                    dados = await value.read()
                    if dados:
                        imagens.append(base64.b64encode(dados).decode("utf-8"))

        produto_data = {
            "nome": str(form.get("nome", "")).strip(),
            "codigo": str(form.get("codigo", "")).strip(),
            "tipoProduto": form.get("tipoProduto", ""),
            "valor": str(form.get("valor", "")),
            "descricao": str(form.get("descricao", "")).strip(),
            "imagens": imagens,
        }

        produto_model = Produto(db)
        if produto_model.create_produto(produto_data):
            return PlainTextResponse("success=1")
        return PlainTextResponse("error=1")
    except Exception as e:
        import logging

        logging.getLogger(__name__).error(f"Erro ao criar produto: {e}")
        return PlainTextResponse("error=1")


@router.post("/produtos/tipo")
async def add_tipo_produto(request: Request, db=Depends(get_db)):
    require_admin(request)
    try:
        form = await request.form()
        descricao = str(form.get("descricao", "")).strip()
        if not descricao:
            return {"success": False, "message": "O nome da categoria é obrigatório."}

        produto_model = Produto(db)
        return produto_model.add_tipo_produto(descricao)
    except Exception as e:
        return {"success": False, "message": f"Erro ao processar solicitação: {e}"}


@router.get("/produtos/{id}/editar", response_class=HTMLResponse)
async def edit_produto_page(request: Request, id: int, db=Depends(get_db)):
    require_admin(request)
    produto_model = Produto(db)
    produto = produto_model.get_produto_by_id(id)
    if not produto:
        return RedirectResponse("/produtos?error=1", status_code=303)
    tipos_produto = produto_model.get_tipos_produto()
    return templates.TemplateResponse(
        request,
        "produtos/edit.html",
        {"request": request, "produto": produto, "tiposProduto": tipos_produto},
    )


@router.post("/produtos/{id}")
async def update_produto(request: Request, id: int, db=Depends(get_db)):
    require_admin(request)
    try:
        form = await request.form()

        imagens = []
        for key, value in form.multi_items():
            if key.startswith("imagens["):
                if hasattr(value, "read"):
                    dados = await value.read()
                    if dados:
                        imagens.append(base64.b64encode(dados).decode("utf-8"))

        imagens_removidas = str(form.get("imagensRemovidas", "")).strip()
        imagens_removidas_list = [i for i in imagens_removidas.split(",") if i] if imagens_removidas else []

        produto_data = {
            "idProduto": id,
            "nome": str(form.get("nome", "")).strip(),
            "codigo": str(form.get("codigo", "")).strip(),
            "tipoProduto": form.get("tipoProduto", ""),
            "valor": str(form.get("valor", "")),
            "descricao": str(form.get("descricao", "")).strip(),
            "visibilidadeProduto": form.get("visibilidadeProduto", 1),
            "imagens": imagens,
            "imagensRemovidas": imagens_removidas_list,
        }

        produto_model = Produto(db)
        if produto_model.update_produto(produto_data):
            return RedirectResponse("/produtos?success=1", status_code=303)
        return RedirectResponse("/produtos?error=1", status_code=303)
    except Exception as e:
        import logging

        logging.getLogger(__name__).error(f"Erro ao atualizar produto: {e}")
        return RedirectResponse("/produtos?error=1", status_code=303)
