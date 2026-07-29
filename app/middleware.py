import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

log = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every HTTP request with method, path, status code, and duration.

    How it works:
    1. Before calling the next handler we clear any leftover context and bind
       a fresh request_id + the request metadata into structlog's contextvars.
    2. We record the start time and call the next handler.

    Normal path (including FastAPI's own 4xx/5xx responses):
       FastAPI's ExceptionMiddleware sits *inside* this middleware, so a 404
       from GET /claims/{id} or a 422 from bad input is already converted to a
       Response by the time call_next returns here.  It reaches the log.info
       line with the correct status code and duration — the except block is
       never entered.

    Unhandled exception path (a genuine crash that bypasses FastAPI's handlers):
       The except block fires, computes duration_ms so timing is still captured,
       logs with log.exception (which includes the traceback), then re-raises so
       Starlette's ServerErrorMiddleware can return a 500.

    4. Context is cleared in both paths so nothing leaks to the next request.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Fresh context for every request
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=str(uuid.uuid4()),
            method=request.method,
            path=request.url.path,
        )

        start = time.perf_counter()

        try:
            response: Response = await call_next(request)
        except Exception:
            # Log unhandled exceptions with duration before re-raising
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            log.exception("unhandled_exception", duration_ms=duration_ms)
            structlog.contextvars.clear_contextvars()
            raise

        # Normal path: log success with duration
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        log.info(
            "http_request",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        # Clean up so context doesn't bleed into background tasks
        structlog.contextvars.clear_contextvars()

        return response
