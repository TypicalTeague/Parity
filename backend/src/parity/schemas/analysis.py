"""Validated analysis request models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from itertools import product
from typing import Annotated, Literal

from pydantic import Field, model_validator

from parity.schemas.common import Classification, DecimalString, Source, StrictModel

InputClassification = Literal["observed", "model_estimated", "simulated", "user_provided"]


class ProbabilityInput(StrictModel):
    value: Annotated[float, Field(ge=0, le=1)]
    classification: InputClassification
    observed_at: datetime
    source: Source

    @model_validator(mode="after")
    def validate_probability(self) -> ProbabilityInput:
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        if self.source.classification.value != self.classification:
            raise ValueError("probability and source classifications must match")
        return self


class ThresholdCondition(StrictModel):
    kind: Literal["threshold"]
    operator: Literal["above", "at_or_above", "below", "at_or_below"]
    threshold: DecimalString
    unit: Annotated[str, Field(min_length=1, max_length=40)]


class EventCondition(StrictModel):
    kind: Literal["named_event"]
    outcome_code: Annotated[str, Field(min_length=1, max_length=80)]


Condition = Annotated[ThresholdCondition | EventCondition, Field(discriminator="kind")]


class ContractLeg(StrictModel):
    leg_id: Annotated[str, Field(pattern=r"^[A-Za-z0-9_-]{1,32}$")]
    market_ticker: Annotated[str, Field(min_length=1, max_length=80)]
    underlying_outcome: Annotated[str, Field(min_length=1, max_length=160)]
    position: Literal["yes", "no"]
    condition: Condition
    settlement_rule: Annotated[str, Field(min_length=1, max_length=120)]
    payoff_contribution: DecimalString
    probability: ProbabilityInput

    @model_validator(mode="after")
    def validate_payoff(self) -> ContractLeg:
        if Decimal(self.payoff_contribution) < 0:
            raise ValueError("payoff_contribution must be non-negative")
        return self


class StatePayoff(StrictModel):
    state: Annotated[list[Literal[0, 1]], Field(min_length=2, max_length=4)]
    payoff: DecimalString

    @model_validator(mode="after")
    def validate_payoff(self) -> StatePayoff:
        if Decimal(self.payoff) < 0:
            raise ValueError("state payoff must be non-negative")
        return self


class ComboDefinition(StrictModel):
    combo_id: Annotated[str, Field(max_length=80)] | None = None
    legs: Annotated[list[ContractLeg], Field(min_length=2, max_length=4)]
    payoff_rule: Literal["all_legs_win", "any_leg_wins", "exactly_one_wins", "state_table"]
    state_payoffs: list[StatePayoff] | None = None
    currency: Literal["USD"]
    payout_unit: Literal["usd_per_contract"]

    @model_validator(mode="after")
    def validate_combo(self) -> ComboDefinition:
        leg_ids = [leg.leg_id for leg in self.legs]
        if len(set(leg_ids)) != len(leg_ids):
            raise ValueError("leg_id values must be unique")
        if self.payoff_rule == "state_table":
            if self.state_payoffs is None:
                raise ValueError("state_table requires state_payoffs")
            states = [tuple(entry.state) for entry in self.state_payoffs]
            expected = set(product((0, 1), repeat=len(self.legs)))
            if any(len(state) != len(self.legs) for state in states):
                raise ValueError("each state must match the leg count")
            if len(states) != len(set(states)):
                raise ValueError("state_payoffs must not contain duplicate states")
            if set(states) != expected:
                raise ValueError(f"state_payoffs must include all {len(expected)} states")
        elif self.state_payoffs is not None:
            raise ValueError("state_payoffs are only valid for the state_table payoff rule")
        return self


class Quote(StrictModel):
    intended_side: Literal["buy", "sell"]
    participant_role: Literal["requester", "quoter", "unknown"]
    price_per_contract: DecimalString
    quantity: Annotated[int, Field(ge=1, le=1_000_000)]
    observed_at: datetime
    source: Source

    @model_validator(mode="after")
    def validate_quote(self) -> Quote:
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        if Decimal(self.price_per_contract) < 0:
            raise ValueError("price_per_contract must be non-negative")
        return self


class LiveMode(StrictModel):
    mode: Literal["live"]


class DeterministicDemoMode(StrictModel):
    mode: Literal["deterministic_demo"]
    fixture_version: Annotated[str, Field(pattern=r"^[A-Za-z0-9._-]+$")]


MarketInputMode = Annotated[LiveMode | DeterministicDemoMode, Field(discriminator="mode")]


class AnalysisRequest(StrictModel):
    combo: ComboDefinition
    quote: Quote
    market_inputs: MarketInputMode


__all__ = [
    "AnalysisRequest",
    "Classification",
    "ComboDefinition",
    "Condition",
    "ContractLeg",
    "DeterministicDemoMode",
    "EventCondition",
    "LiveMode",
    "MarketInputMode",
    "ProbabilityInput",
    "Quote",
    "StatePayoff",
    "ThresholdCondition",
]
