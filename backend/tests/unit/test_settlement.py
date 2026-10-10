from datetime import UTC, datetime
from decimal import Decimal

import pytest

from parity.domain.settlement import independence_distribution, payoff_table
from parity.schemas.analysis import (
    ComboDefinition,
    ContractLeg,
    EventCondition,
    ProbabilityInput,
    StatePayoff,
)
from parity.schemas.common import Classification, Source, SourceKind

NOW = datetime(2026, 10, 10, tzinfo=UTC)


def leg(leg_id: str, probability: float) -> ContractLeg:
    source = Source(
        source_id="fixture",
        source_name="Test fixture",
        source_kind=SourceKind.DETERMINISTIC_FIXTURE,
        classification=Classification.SIMULATED,
        fixture_version="test-v1",
    )
    return ContractLeg(
        leg_id=leg_id,
        market_ticker=leg_id,
        underlying_outcome=leg_id,
        position="yes",
        condition=EventCondition(kind="named_event", outcome_code=leg_id),
        settlement_rule="binary-v1",
        payoff_contribution="1.00",
        probability=ProbabilityInput(
            value=probability,
            classification="simulated",
            observed_at=NOW,
            source=source,
        ),
    )


def combo(rule: str, state_payoffs: list[StatePayoff] | None = None) -> ComboDefinition:
    return ComboDefinition(
        legs=[leg("a", 0.6), leg("b", 0.5)],
        payoff_rule=rule,
        state_payoffs=state_payoffs,
        currency="USD",
        payout_unit="usd_per_contract",
    )


def test_independence_distribution_is_complete_and_normalized() -> None:
    distribution = independence_distribution([0.6, 0.5])
    assert distribution == {
        (0, 0): pytest.approx(0.2),
        (0, 1): pytest.approx(0.2),
        (1, 0): pytest.approx(0.3),
        (1, 1): pytest.approx(0.3),
    }
    assert sum(distribution.values()) == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("rule", "winning_states"),
    [
        ("all_legs_win", {(1, 1)}),
        ("any_leg_wins", {(0, 1), (1, 0), (1, 1)}),
        ("exactly_one_wins", {(0, 1), (1, 0)}),
    ],
)
def test_builtin_payoff_rules_are_unit_payoffs(
    rule: str, winning_states: set[tuple[int, ...]]
) -> None:
    table = payoff_table(combo(rule))
    assert {state for state, value in table.items() if value == Decimal("1")} == winning_states
    assert set(table.values()) <= {Decimal("0"), Decimal("1")}


def test_explicit_state_table_preserves_non_binary_payoffs() -> None:
    entries = [
        StatePayoff(state=[0, 0], payoff="0.00"),
        StatePayoff(state=[0, 1], payoff="0.25"),
        StatePayoff(state=[1, 0], payoff="0.75"),
        StatePayoff(state=[1, 1], payoff="1.50"),
    ]
    assert payoff_table(combo("state_table", entries))[(1, 1)] == Decimal("1.50")
