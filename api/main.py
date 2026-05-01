"""
API entrypoint: run from the `api/` directory:

    python main.py

Or: python -m uvicorn main:app --reload --host 0.0.0.0 --port 3001
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.config import settings
from app.cors_util import get_allowed_origins
from app.errors import validation_exception_handler
from app.middleware import CorpMiddleware, RequestLogMiddleware
from app.routers import api as api_router
from app.routers import health as health_router
from app.services.registry import LimiterRegistry

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.registry = LimiterRegistry()
    yield


app = FastAPI(title="Rate limiter showcase API", lifespan=lifespan)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.add_middleware(RequestLogMiddleware)
app.add_middleware(CorpMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=500)

_allowed_origins = get_allowed_origins()
if _allowed_origins:
    logger.info("[cors] allowed origins: %s", ", ".join(_allowed_origins))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    logger.warning("[cors] no CLIENT_ORIGIN / dev defaults; allowing * without credentials")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(health_router.router)
app.include_router(api_router.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
    )
