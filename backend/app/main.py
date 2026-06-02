from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.db.session import SessionLocal
from app.services.admin_seed import seed_admin_if_empty


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging(settings.app_log_level)
    try:
        async with SessionLocal() as session:
            await seed_admin_if_empty(session)
    except Exception:  # noqa: S110
        pass
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Inventory & Order Management API",
        version="0.1.0",
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
    app.add_exception_handler(HTTPException, _http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)
    app.add_exception_handler(RequestValidationError, _validation_exception_handler)
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix="/api/v1")
    return app


def _request_id_from(request: Request) -> str | None:
    value = request.headers.get("x-request-id")
    return value if value else None


async def _http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": "Internal server error"}},
        )
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail:
        code = str(detail.get("code"))
        message = str(detail.get("message", ""))
        extra_details = detail.get("details")
    else:
        code = _default_code_for(exc.status_code)
        message = str(detail) if detail else _default_message_for(exc.status_code)
        extra_details = None
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if extra_details is not None:
        payload["error"]["details"] = extra_details
    request_id = _request_id_from(request)
    if request_id:
        payload["error"]["request_id"] = request_id
    return JSONResponse(status_code=exc.status_code, content=payload)


async def _validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    errors = exc.errors() if isinstance(exc, RequestValidationError) else []
    payload: dict[str, Any] = {
        "error": {
            "code": "validation_error",
            "message": "Request validation failed",
            "details": errors,
        }
    }
    request_id = _request_id_from(request)
    if request_id:
        payload["error"]["request_id"] = request_id
    return JSONResponse(status_code=422, content=payload)


async def _rate_limit_handler(request: Request, exc: Exception) -> JSONResponse:
    detail = str(exc) if isinstance(exc, RateLimitExceeded) else "Too many requests"
    payload: dict[str, Any] = {
        "error": {
            "code": "rate_limited",
            "message": "Too many requests",
            "details": [detail],
        }
    }
    request_id = _request_id_from(request)
    if request_id:
        payload["error"]["request_id"] = request_id
    return JSONResponse(status_code=429, content=payload)


def _default_code_for(status_code: int) -> str:
    mapping = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        422: "validation_error",
        429: "rate_limited",
    }
    return mapping.get(status_code, "http_error")


def _default_message_for(status_code: int) -> str:
    mapping = {
        400: "Bad request",
        401: "Not authenticated",
        403: "Forbidden",
        404: "Not found",
        409: "Conflict",
        429: "Too many requests",
    }
    return mapping.get(status_code, "Request failed")


app = create_app()
