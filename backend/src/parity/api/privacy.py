"""Privacy-safe request metadata logging and response cache controls."""

from __future__ import annotations

import logging
from time import perf_counter

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import RequestResponseEndpoint

logger = logging.getLogger("parity.http")

NO_STORE_HEADERS = {
    "Cache-Control": "no-store, private, max-age=0, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
}


def install_privacy_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def privacy_boundary(request: Request, call_next: RequestResponseEndpoint) -> Response:
        started = perf_counter()
        response = await call_next(request)
        route = request.scope.get("route")
        route_path = getattr(route, "path", "unmatched")
        logger.info(
            "http_request_completed route=%s status=%d duration_ms=%d",
            route_path,
            response.status_code,
            round((perf_counter() - started) * 1000),
        )
        if request.url.path == "/api/v1/analyses":
            response.headers.update(NO_STORE_HEADERS)
        return response
