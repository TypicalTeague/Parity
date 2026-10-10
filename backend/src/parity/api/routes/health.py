"""Minimal service health route."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

router = APIRouter()


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["ok"] = "ok"


@router.get("/health", operation_id="getHealth", response_model=HealthResponse)
def get_health() -> HealthResponse:
    return HealthResponse()
