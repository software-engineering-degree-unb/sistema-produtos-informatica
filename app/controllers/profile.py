from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.templating import templates

from app.dependencies import get_db
from app.functions.session_timeout import require_login
from app.models.usuario import Usuario

router = APIRouter()



@router.get("/perfil", response_class=HTMLResponse)
async def index(request: Request, db=Depends(get_db)):
    require_login(request)

    usuario_model = Usuario(db)
    user_details = usuario_model.get_by_id(request.session["id"])

    return templates.TemplateResponse(
        request,
        "profile/index.html", {"request": request, "userDetails": user_details}
    )
