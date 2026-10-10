from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from parity.schemas.analysis import (
    AnalysisRequest,
    ComboDefinition,
    ContractLeg,
    DeterministicDemoMode,
    EventCondition,
    ProbabilityInput,
    Quote,
    StatePayoff,
)
from parity.schemas.common import Classification, Source, SourceKind

NOW = datetime(2026, 10, 10, tzinfo=UTC)


def source(classification: Classification = Classification.SIMULATED) -> Source:
    return Source(
        source_id="canonical-v1",
        source_name="Canonical deterministic fixture",
        source_kind=SourceKind.DETERMINISTIC_FIXTURE,
        classification=classification,
        observed_at=NOW,
        fixture_version="canonical-v1",
    )


def leg(leg_id: str) -> ContractLeg:
    return ContractLeg(
        leg_id=leg_id,
        market_ticker=f"TEST-{leg_id}",
        underlying_outcome=leg_id,
        position="yes",
        condition=EventCondition(kind="named_event", outcome_code=leg_id),
        settlement_rule="binary-v1",
        payoff_contribution="1.00",
        probability=ProbabilityInput(
            value=0.5,
            classification=Classification.SIMULATED,
            observed_at=NOW,
            source=source(),
        ),
    )


def quote() -> Quote:
    return Quote(
        intended_side="buy",
        participant_role="requester",
        price_per_contract="0.45",
        quantity=2,
        observed_at=NOW,
        source=Source(
            source_id="request",
            source_name="Submitted quote",
            source_kind=SourceKind.USER_INPUT,
            classification=Classification.USER_PROVIDED,
        ),
    )


def test_valid_request_is_strict_and_timezone_aware() -> None:
    request = AnalysisRequest(
        combo=ComboDefinition(
            legs=[leg("a"), leg("b")],
            payoff_rule="all_legs_win",
            currency="USD",
            payout_unit="usd_per_contract",
        ),
        quote=quote(),
        market_inputs=DeterministicDemoMode(
            mode="deterministic_demo", fixture_version="canonical-v1"
        ),
    )
    assert request.combo.legs[0].probability.observed_at.tzinfo is UTC
    with pytest.raises(ValidationError, match="extra_forbidden"):
        AnalysisRequest.model_validate({**request.model_dump(), "secret": "must-not-pass"})


def test_naive_timestamp_is_rejected() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        ProbabilityInput(
            value=0.5,
            classification=Classification.SIMULATED,
            observed_at=datetime(2026, 10, 10),
            source=source(),
        )


def test_duplicate_legs_are_rejected() -> None:
    with pytest.raises(ValidationError, match="unique"):
        ComboDefinition(
            legs=[leg("a"), leg("a")],
            payoff_rule="all_legs_win",
            currency="USD",
            payout_unit="usd_per_contract",
        )


def test_state_table_must_cover_every_state_once() -> None:
    incomplete = [StatePayoff(state=[0, 0], payoff="0.00")]
    with pytest.raises(ValidationError, match="all 4 states"):
        ComboDefinition(
            legs=[leg("a"), leg("b")],
            payoff_rule="state_table",
            state_payoffs=incomplete,
            currency="USD",
            payout_unit="usd_per_contract",
        )


@pytest.mark.parametrize("money", ["01.0", ".5", "1.", "nan", "1e-2"])
def test_money_requires_canonical_decimal_string(money: str) -> None:
    with pytest.raises(ValidationError):
        Quote(
            intended_side="buy",
            participant_role="requester",
            price_per_contract=money,
            quantity=1,
            observed_at=NOW,
            source=source(Classification.USER_PROVIDED),
        )
