from fastapi import FastAPI

from .middleware import register_middleware
from .routes import register_routes
from .lifecycle import register_lifecycle


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title="LangGraph Enterprise Agent Platform",
        version="1.0.0",
    )

    register_middleware(app)
    register_routes(app)
    register_lifecycle(app)

    return app
