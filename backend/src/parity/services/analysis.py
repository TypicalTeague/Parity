"""Request-local orchestration for one explainable price waterfall."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from decimal import ROUND_HALF_EVEN, Decimal
from importlib.resources import files
from typing import Any

import numpy as np

from parity.api.errors import DomainError
from parity.domain.correlation import joint_state_probabilities
from parity.domain.pricing import quote_difference
from parity.domain.settlement import expected_payoff, independence_distribution, payoff_table
from parity.schemas.analysis import AnalysisRequest, DeterministicDemoMode
from parity.schemas.common import Classification, Source, SourceKind, Unit
from parity.schemas.results import (
    AnalysisResponse,
    AvailableValue,
    CorrelationAdjustment,
    FeeAssessment,
    HistoricalWindow,
    IntegrationMetadata,
    Precision,
    UnavailableValue,
    Waterfall,
)

SIX_PLACES = Decimal("0.000001")


def _load_fixture(version: str) -> tuple[dict[str, Any], str]:
    if version != "canonical-v1":
        raise DomainError(
            code="UNSUPPORTED_COMBO",
            message="The requested deterministic fixture is not supported.",
        )
    path = files("parity.fixtures").joinpath(f"{version}.json")
    payload = path.read_bytes()
    return json.loads(payload), hashlib.sha256(payload).hexdigest()


def _money(value: Decimal, classification: Classification) -> AvailableValue:
    return AvailableValue(
        value=str(value.quantize(SIX_PLACES, rounding=ROUND_HALF_EVEN)),
        unit=Unit.USD_PER_CONTRACT,
        classification=classification,
        precision=Precision(decimal_places=6, rounding_mode="half_even"),
    )


def analyze(request: AnalysisRequest) -> AnalysisResponse:
    if not isinstance(request.market_inputs, DeterministicDemoMode):
        raise DomainError(
            code="LIVE_DATA_UNAVAILABLE",
            message="Live public data is not available in this implementation increment.",
            status_code=503,
            fallback={"scenario_id": "canonical-v1", "requires_explicit_request": True},
        )

    fixture, fixture_hash = _load_fixture(request.market_inputs.fixture_version)
    matrix = np.asarray(fixture["correlation_matrix"], dtype=float)
    if matrix.shape != (len(request.combo.legs), len(request.combo.legs)):
        raise DomainError(
            code="UNSUPPORTED_COMBO",
            message="This deterministic fixture supports exactly two legs.",
        )

    probabilities = [leg.probability.value for leg in request.combo.legs]
    payoffs = payoff_table(request.combo)
    independent = expected_payoff(independence_distribution(probabilities), payoffs)
    joint = joint_state_probabilities(probabilities, matrix, seed=int(fixture["seed"]))
    fair_value = expected_payoff(joint, payoffs)
    adjustment = fair_value - independent
    quoted_price = Decimal(request.quote.price_per_contract)
    difference = quote_difference(fair_value, quoted_price, request.quote.intended_side)

    unavailable_fee = UnavailableValue(
        unit=Unit.USD_TOTAL,
        reason_code="FEE_POLICY_NOT_VERIFIED",
    )
    fee = FeeAssessment(
        status="unavailable",
        total_fee=unavailable_fee,
        assumptions=[],
        unavailable_reason=(
            "No current fee rule and RFQ-role scope have been verified for this fixture."
        ),
    )
    window = fixture["historical_window"]
    correlation = CorrelationAdjustment(
        status="coherent",
        original_matrix=matrix.tolist(),
        used_matrix=matrix.tolist(),
        historical_window=HistoricalWindow(
            start=datetime.fromisoformat(window["start"].replace("Z", "+00:00")),
            end=datetime.fromisoformat(window["end"].replace("Z", "+00:00")),
        ),
        observation_count=int(fixture["observation_count"]),
        missing_data_treatment=str(fixture["missing_data_treatment"]),
        outcome_transformations=list(fixture["outcome_transformations"]),
        integration=IntegrationMetadata(
            method="scipy_mvn_rectangle",
            seed=int(fixture["seed"]),
            state_order="lexicographic",
            maxpts=1_000_000,
            abseps=1e-8,
            releps=1e-8,
            probability_sum_residual=sum(joint.values()) - 1.0,
            maximum_correction=0.0,
        ),
        limitations=[
            "Gaussian-copula dependence is a model estimate, not an objectively correct "
            "probability."
        ],
    )
    provenance = Source(
        source_id="canonical-v1",
        source_name="Canonical deterministic fixture",
        source_kind=SourceKind.DETERMINISTIC_FIXTURE,
        classification=Classification.SIMULATED,
        observed_at=max(leg.probability.observed_at for leg in request.combo.legs),
        fixture_version="canonical-v1",
        content_sha256=fixture_hash,
        limitations=["Fixture values are simulated and are not current market observations."],
    )
    return AnalysisResponse(
        waterfall=Waterfall(
            independence_baseline=_money(independent, Classification.MODEL_ESTIMATED),
            correlation_adjustment=_money(adjustment, Classification.ADJUSTED),
            model_fair_value=_money(fair_value, Classification.MODEL_ESTIMATED),
            quote_difference=_money(difference, Classification.MODEL_ESTIMATED),
            fees=fee,
            net_expected_value=UnavailableValue(
                unit=Unit.USD_TOTAL,
                reason_code="FEE_POLICY_NOT_VERIFIED",
            ),
        ),
        correlation=correlation,
        provenance=[provenance],
        observation_time=provenance.observed_at,
        model_version=str(fixture["model_version"]),
        configuration_version=str(fixture["configuration_version"]),
        fallback_used=True,
        disclosures=[
            "Parity estimates fair value; it does not establish objectively correct probabilities.",
            "The quote difference is not guaranteed profit or guaranteed market-maker profit.",
            "Fee-adjusted net expected value is unavailable until the applicable fee is verified.",
        ],
    )
