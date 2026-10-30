"""FastAPI routes; persistence and authentication live in separate services."""

import hashlib
import hmac
import logging
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal, cast

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool

from ai_bdd_demo.auth import ERROR, Authentication, Clock, Services, Sessions, SystemClock
from ai_bdd_demo.config import AppSettings, Settings, validate
from ai_bdd_demo.db import Database, Members

LOGGER = logging.getLogger(__name__)
SESSION_COOKIE = "session_id"
CSRF_COOKIE = "csrf_proof"
ROOT = Path(__file__).resolve().parent


def create_app_from_environment() -> FastAPI:
    """Optional Uvicorn factory; all runtime policies must be supplied externally."""
    return create_app(settings=AppSettings.from_environment())


def create_app(*, settings: Settings, clock: Clock | None = None) -> FastAPI:
    validate(settings)
    time_source = clock if clock is not None else SystemClock()
    database = Database(Path(settings.database_path))
    templates = Jinja2Templates(directory=str(ROOT / "templates"))

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        database.initialize()
        members = Members(database)
        sessions = Sessions(database, time_source, settings.session_ttl_seconds)
        app.state.services = Services(members, Authentication(database, members, sessions, time_source),
                                      sessions)
        yield
        # Connections are operation-scoped and always closed by Database.connection.
        del app.state.services

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")

    def signature(nonce: str) -> str:
        return hmac.new(settings.secret_key.encode(), nonce.encode(), hashlib.sha256).hexdigest()

    def valid_proof(value: str) -> bool:
        if len(value) != 129 or not value.isascii():
            return False
        nonce, separator, supplied = value.partition(".")
        return separator == "." and hmac.compare_digest(signature(nonce), supplied)

    def set_cookie(response: Response, name: str, value: str) -> None:
        response.set_cookie(name, value, httponly=True, secure=settings.cookie_secure,
                            samesite=cast(Literal["lax", "strict", "none"], settings.cookie_samesite),
                            path="/")

    def login_html(request: Request, message: str = "", *, status: int = 200) -> Response:
        proof = request.cookies.get(CSRF_COOKIE, "")
        if not valid_proof(proof):
            nonce = secrets.token_hex(32)
            proof = f"{nonce}.{signature(nonce)}"
        response = templates.TemplateResponse(request=request, name="login.html", context={
            "csrf_token": proof, "message": message,
        }, status_code=status)
        set_cookie(response, CSRF_COOKIE, proof)
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/", include_in_schema=False)
    def index() -> RedirectResponse:
        return RedirectResponse("/login", status_code=303)

    @app.get("/login", response_class=HTMLResponse)
    def login_page(request: Request) -> Response:
        return login_html(request)

    @app.post("/login", response_class=HTMLResponse)
    async def login(request: Request) -> Response:
        form = await request.form()
        proof = form.get("csrf_token")
        cookie = request.cookies.get(CSRF_COOKIE, "")
        if not isinstance(proof, str) or not valid_proof(proof) or not hmac.compare_digest(proof, cookie):
            return HTMLResponse("請重新開啟登入頁後再試。", status_code=403,
                                headers={"Cache-Control": "no-store"})
        username, password = form.get("username"), form.get("password")
        if not isinstance(username, str) or not isinstance(password, str):
            return login_html(request, ERROR)
        # Do not normalize credentials or echo user input into error messages.
        result = await run_in_threadpool(app.state.services.auth.authenticate, username, password)
        if result.session_id is None:
            return login_html(request, result.message)
        response = RedirectResponse("/welcome", status_code=303)
        set_cookie(response, SESSION_COOKIE, result.session_id)
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/welcome", response_class=HTMLResponse)
    def welcome(request: Request) -> Response:
        session = app.state.services.sessions.get(request.cookies.get(SESSION_COOKIE, ""))
        if session is None:
            return RedirectResponse("/login", status_code=303, headers={"Cache-Control": "no-store"})
        return templates.TemplateResponse(request=request, name="welcome.html", context={
            "username": session.username,
        }, headers={"Cache-Control": "no-store"})

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> Response:
        # Avoid logging exception text/locals: they may contain credentials or secrets.
        LOGGER.error("Application request failed")
        return HTMLResponse("系統暫時無法處理請求，請稍後再試。", status_code=500,
                            headers={"Cache-Control": "no-store"})

    return app
