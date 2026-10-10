"""Settlement-state enumeration and independence probabilities."""

from __future__ import annotations

from decimal import Decimal
from itertools import product
from math import prod

from parity.schemas.analysis import ComboDefinition

State = tuple[int, ...]


def states(leg_count: int) -> tuple[State, ...]:
    if not 2 <= leg_count <= 4:
        raise ValueError("supported combos contain two to four legs")
    return tuple(product((0, 1), repeat=leg_count))


def independence_distribution(probabilities: list[float]) -> dict[State, float]:
    """Return every joint-state probability under independent Bernoulli marginals."""
    if not 2 <= len(probabilities) <= 4:
        raise ValueError("supported combos contain two to four probabilities")
    if any(not 0 <= probability <= 1 for probability in probabilities):
        raise ValueError("probabilities must be between 0 and 1")
    return {
        state: prod(
            probability if outcome else 1.0 - probability
            for probability, outcome in zip(probabilities, state, strict=True)
        )
        for state in states(len(probabilities))
    }


def payoff_table(combo: ComboDefinition) -> dict[State, Decimal]:
    """Map every supported settlement state to its declared per-contract payoff."""
    all_states = states(len(combo.legs))
    if combo.payoff_rule == "state_table":
        if combo.state_payoffs is None:  # protected by schema validation; defensive for callers
            raise ValueError("state_table requires state_payoffs")
        return {tuple(entry.state): Decimal(entry.payoff) for entry in combo.state_payoffs}

    def wins(state: State) -> bool:
        if combo.payoff_rule == "all_legs_win":
            return all(state)
        if combo.payoff_rule == "any_leg_wins":
            return any(state)
        return sum(state) == 1

    return {state: Decimal(1 if wins(state) else 0) for state in all_states}


def expected_payoff(distribution: dict[State, float], payoffs: dict[State, Decimal]) -> Decimal:
    if set(distribution) != set(payoffs):
        raise ValueError("distribution and payoff states must match")
    return sum(
        (Decimal(str(distribution[state])) * payoffs[state] for state in sorted(distribution)),
        start=Decimal(0),
    )
