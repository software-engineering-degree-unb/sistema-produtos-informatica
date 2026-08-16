import os

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config.settings import SECRET_KEY
from app.controllers import admin, auth, compra, home, produto, profile
from app.functions.session_timeout import RedirectException

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="Sistema de Produtos de Informática")

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, same_site="lax")

app.mount("/assets", StaticFiles(directory=os.path.join(BASE_DIR, "public", "assets")), name="assets")


@app.exception_handler(RedirectException)
async def redirect_exception_handler(request: Request, exc: RedirectException):
    return RedirectResponse(url=exc.url)


app.include_router(auth.router)
app.include_router(home.router)
app.include_router(admin.router)
app.include_router(produto.router)
app.include_router(compra.router)
app.include_router(profile.router)
