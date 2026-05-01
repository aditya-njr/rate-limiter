import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("uvicorn.error")


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            "[http] %s %s %s %sms",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response


class CorpMiddleware(BaseHTTPMiddleware):
    """Mirror Helmet crossOriginResourcePolicy: cross-origin."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        return response
