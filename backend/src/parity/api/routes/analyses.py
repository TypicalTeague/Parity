"""Stateless price-waterfall endpoint."""

from fastapi import APIRouter

from parity.schemas.analysis import AnalysisRequest
from parity.schemas.results import AnalysisResponse, ErrorResponse
from parity.services.analysis import analyze

router = APIRouter()


@router.post(
    "/analyses",
    operation_id="analyzeCombo",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
def analyze_combo(request: AnalysisRequest) -> AnalysisResponse:
    return analyze(request)
