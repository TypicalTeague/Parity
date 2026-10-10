"""Result and error schemas shared by the API and OpenAPI export."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field, model_validator

from parity.schemas.common import Classification, DecimalString, Source, StrictModel, Unit


class Precision(StrictModel):
    decimal_places: Annotated[int, Field(ge=0, le=12)]
    rounding_mode: Literal["half_even", "ceiling", "exchange_rule"]


class AvailableValue(StrictModel):
    available: Literal[True] = True
    value: float | DecimalString
    unit: Unit
    classification: Classification
    precision: Precision

    @model_validator(mode="after")
    def validate_available(self) -> AvailableValue:
        if self.classification is Classification.UNAVAILABLE:
            raise ValueError("available values cannot use the unavailable classification")
        return self


class UnavailableValue(StrictModel):
    available: Literal[False] = False
    unit: Unit
    classification: Literal["unavailable"] = "unavailable"
    reason_code: Annotated[str, Field(min_length=1, max_length=80)]


ClassifiedValue = Annotated[AvailableValue | UnavailableValue, Field(discriminator="available")]


class MatrixAdjustment(StrictModel):
    method: Literal["higham_dykstra"]
    iterations: Annotated[int, Field(ge=1)]
    converged: bool
    original_min_eigenvalue: float
    repaired_min_eigenvalue: float
    frobenius_norm: Annotated[float, Field(ge=0)]
    max_entry_change: Annotated[float, Field(ge=0)]
    acceptance_threshold: Annotated[float, Field(ge=0)]


class IntegrationMetadata(StrictModel):
    method: Literal["scipy_mvn_rectangle"]
    seed: int
    state_order: Literal["lexicographic"]
    maxpts: Annotated[int, Field(ge=1)]
    abseps: Annotated[float, Field(gt=0)]
    releps: Annotated[float, Field(gt=0)]
    probability_sum_residual: float | None = None
    maximum_correction: Annotated[float, Field(ge=0)] | None = None


class HistoricalWindow(StrictModel):
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def validate_window(self) -> HistoricalWindow:
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ValueError("historical window timestamps must be timezone-aware")
        if self.start >= self.end:
            raise ValueError("historical window start must precede end")
        return self


class CorrelationAdjustment(StrictModel):
    status: Literal["coherent", "adjusted", "unavailable"]
    original_matrix: list[list[float]] | None
    used_matrix: list[list[float]] | None
    historical_window: HistoricalWindow
    observation_count: Annotated[int, Field(ge=0)]
    missing_data_treatment: str
    outcome_transformations: list[str]
    matrix_adjustment: MatrixAdjustment | None = None
    integration: IntegrationMetadata
    limitations: list[str] = Field(default_factory=list)


class FeeAssessment(StrictModel):
    status: Literal["verified", "estimated", "unavailable"]
    fee_role: Literal["maker", "taker"] | None = None
    policy_source: Source | None = None
    formula_version: str | None = None
    multiplier: DecimalString | None = None
    model_trade_fee: ClassifiedValue | None = None
    balance_rounding_fee: ClassifiedValue | None = None
    rebate: ClassifiedValue | None = None
    total_fee: ClassifiedValue
    assumptions: list[str] = Field(default_factory=list)
    unavailable_reason: str | None = None


class Waterfall(StrictModel):
    independence_baseline: ClassifiedValue
    correlation_adjustment: ClassifiedValue
    model_fair_value: ClassifiedValue
    quote_difference: ClassifiedValue
    fees: FeeAssessment
    net_expected_value: ClassifiedValue


class ValidationSummary(StrictModel):
    status: Literal["available", "insufficient_evidence"]
    fitting_window: str
    evaluation_window: str
    eligible_count: Annotated[int, Field(ge=0)]
    excluded_count: Annotated[int, Field(ge=0)]
    prediction_count: Annotated[int, Field(ge=0)]
    metrics: dict[str, Annotated[float, Field(ge=0)]]
    limitations: list[str] = Field(default_factory=list)
    no_guarantee_disclosure: Annotated[str, Field(min_length=1)]


class AnalysisResponse(StrictModel):
    waterfall: Waterfall
    correlation: CorrelationAdjustment
    validation_summary: ValidationSummary | None = None
    provenance: Annotated[list[Source], Field(min_length=1)]
    observation_time: datetime
    model_version: Annotated[str, Field(min_length=1)]
    configuration_version: Annotated[str, Field(min_length=1)]
    fallback_used: bool
    disclosures: Annotated[list[str], Field(min_length=1)]


class ErrorField(StrictModel):
    path: list[str]
    code: Annotated[str, Field(min_length=1, max_length=80)]
    message: Annotated[str, Field(min_length=1, max_length=240)]


class ErrorDetail(StrictModel):
    code: Literal[
        "VALIDATION_FAILED",
        "UNSUPPORTED_COMBO",
        "DEPENDENCE_UNUSABLE",
        "LIVE_DATA_UNAVAILABLE",
        "INTERNAL_ERROR",
    ]
    message: Annotated[str, Field(min_length=1, max_length=240)]
    fields: list[ErrorField] = Field(default_factory=list)
    fallback: dict[str, str | bool] | None = None


class ErrorResponse(StrictModel):
    error: ErrorDetail
