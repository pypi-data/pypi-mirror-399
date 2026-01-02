from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from langgraph_enterprise_sdk.observability.logging import get_logger


logger = get_logger("server")


def register_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def error_handler(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logger.error(
                "request_failed",
                path=request.url.path,
                error=str(exc),
            )
            return JSONResponse(
                status_code=500,
                content={"error": str(exc)},
            )
