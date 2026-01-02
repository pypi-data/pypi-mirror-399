from fastapi import FastAPI

from langgraph_enterprise_sdk.observability.logging import get_logger


logger = get_logger("lifecycle")


def register_lifecycle(app: FastAPI) -> None:
    @app.on_event("startup")
    async def on_startup():
        logger.info("server_startup")

    @app.on_event("shutdown")
    async def on_shutdown():
        logger.info("server_shutdown")
