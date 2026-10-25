from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from rgb_website.api import health_router
from rgb_website.api.admin import router as admin_router
from rgb_website.api.experiment import router as experiment_router

STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    app = FastAPI(
        title="ColorEmotionStudy",
        description=(
            "Datensparsame Forschungsanwendung zur Zuordnung von Farben und Emotionen."
        ),
        version="0.1.0",
    )
    app.include_router(health_router)
    app.include_router(experiment_router)
    app.include_router(admin_router)

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("Cache-Control", "no-store")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; form-action 'self'; "
            "base-uri 'none'; frame-ancestors 'none'",
        )
        return response

    app.add_api_route(
        "/admin",
        lambda: FileResponse(STATIC_DIR / "admin.html"),
        include_in_schema=False,
    )
    app.add_api_route(
        "/impressum",
        lambda: FileResponse(STATIC_DIR / "impressum.html"),
        include_in_schema=False,
    )
    app.add_api_route(
        "/datenschutz",
        lambda: FileResponse(STATIC_DIR / "datenschutz.html"),
        include_in_schema=False,
    )
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="web")
    return app


app = create_app()
