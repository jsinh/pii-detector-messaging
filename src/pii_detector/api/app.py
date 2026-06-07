from fastapi import FastAPI

from pii_detector.api.routers import detect, health
from pii_detector.core.config import get_settings


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
    )

    app.include_router(health.router)
    app.include_router(detect.router)

    return app


# Module-level instance for `fastapi dev` / `fastapi run` to import.
app = create_app()
