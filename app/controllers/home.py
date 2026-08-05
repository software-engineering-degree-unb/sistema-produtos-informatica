from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.templating import templates

from app.dependencies import get_db
from app.functions.session_timeout import RedirectException, require_login

router = APIRouter()



@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db=Depends(get_db)):
    require_login(request)

    if request.session["idTipoLogin"] == 1:
        return templates.TemplateResponse(request,
        "home/usuario.html", {"request": request})

    return templates.TemplateResponse(request,
        "home/admin.html", {"request": request})
