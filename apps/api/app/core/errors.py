"""One error envelope for every failure.

{"error": {"code": "...", "message": "...", "details": {}, "request_id": "..."}}
"""

import logging
from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.request_context import get_request_id

logger = logging.getLogger("app.errors")

_STATUS_CODES: dict[int, str] = {
    400: "bad_request",
    401: "unauthenticated",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    413: "payload_too_large",
    415: "unsupported_media_type",
    422: "validation_error",
    429: "rate_limited",
}


class AppError(Exception):
    """Base class for expected, client-visible errors."""

    status_code = 500
    code = "internal_error"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        self.details: dict[str, Any] = dict(details or {})
        self.headers: dict[str, str] = dict(headers or {})


class UnauthenticatedError(AppError):
    status_code = 401
    code = "unauthenticated"


class ForbiddenError(AppError):
    status_code = 403
    code = "forbidden"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class RateLimitedError(AppError):
    status_code = 429
    code = "rate_limited"


class ServiceUnavailableError(AppError):
    status_code = 503
    code = "service_unavailable"


def build_error_body(
    code: str,
    message: str,
    details: Mapping[str, Any] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": dict(details or {}),
            "request_id": request_id if request_id is not None else get_request_id(),
        }
    }


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
    request_id: str | None = None,
) -> JSONResponse:
    response_headers = dict(headers or {})
    rid = request_id if request_id is not None else get_request_id()
    if rid:
        response_headers.setdefault("X-Request-ID", rid)
    return JSONResponse(
        status_code=status_code,
        content=build_error_body(code, message, details, rid),
        headers=response_headers,
    )


def _request_id_from(request: Request) -> str | None:
    state_value = getattr(request.state, "request_id", None)
    return state_value if isinstance(state_value, str) else get_request_id()


async def _handle_app_error(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, AppError):
        raise exc
    return error_response(
        exc.status_code, exc.code, exc.message, exc.details, exc.headers, _request_id_from(request)
    )


async def _handle_validation_error(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):
        raise exc
    errors = []
    for item in exc.errors():
        location = [
            str(part) for part in item.get("loc", ()) if part not in ("body", "query", "path")
        ]
        errors.append({"field": ".".join(location), "issue": str(item.get("msg", "invalid value"))})
    return error_response(
        422,
        "validation_error",
        "The request contains invalid data.",
        {"errors": errors},
        request_id=_request_id_from(request),
    )


async def _handle_http_exception(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, StarletteHTTPException):
        raise exc
    code = _STATUS_CODES.get(
        exc.status_code, "server_error" if exc.status_code >= 500 else "http_error"
    )
    message = exc.detail if isinstance(exc.detail, str) else "The request could not be completed."
    headers = dict(exc.headers) if exc.headers else None
    return error_response(exc.status_code, code, message, None, headers, _request_id_from(request))


async def _handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
    rid = _request_id_from(request)
    logger.error(
        "unhandled_exception",
        exc_info=exc,
        extra={"path": request.url.path, "method": request.method},
    )
    return error_response(
        500, "internal_error", "Something went wrong on our side.", request_id=rid
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _handle_app_error)
    app.add_exception_handler(RequestValidationError, _handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, _handle_http_exception)
    app.add_exception_handler(Exception, _handle_unexpected)
