"""Sanitized public error mapping that never echoes submitted values."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from parity.api.privacy import NO_STORE_HEADERS
from parity.schemas.results import ErrorDetail, ErrorField, ErrorResponse

logger = logging.getLogger("parity.errors")

ErrorCode = Literal[
    "VALIDATION_FAILED",
    "UNSUPPORTED_COMBO",
    "DEPENDENCE_UNUSABLE",
    "LIVE_DATA_UNAVAILABLE",
    "INTERNAL_ERROR",
]


@dataclass(slots=True)
class DomainError(Exception):
    code: ErrorCode
    message: str
    status_code: int = 400
    fields: list[ErrorField] = field(default_factory=list)


def _response(status_code: int, detail: ErrorDetail) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(error=detail).model_dump(mode="json"),
        headers=NO_STORE_HEADERS,
    )


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        fields = [
            ErrorField(
                path=[str(part) for part in item.get("loc", ()) if part != "body"],
                code=str(item.get("type", "invalid"))[:80],
                message="Invalid value for this field.",
            )
            for item in exc.errors()
        ]
        return _response(
            422,
            ErrorDetail(
                code="VALIDATION_FAILED",
                message="The request did not pass validation.",
                fields=fields,
            ),
        )

    @app.exception_handler(DomainError)
    async def domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return _response(
            exc.status_code,
            ErrorDetail(code=exc.code, message=exc.message, fields=exc.fields),
        )

    @app.exception_handler(Exception)
    async def internal_error(_: Request, __: Exception) -> JSONResponse:
        logger.error("internal_error code=INTERNAL_ERROR")
        return _response(
            500,
            ErrorDetail(
                code="INTERNAL_ERROR",
                message="The analysis could not be completed.",
                fields=[],
            ),
        )
