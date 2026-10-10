"""Fee formula engine; applicable policies are supplied as verified evidence."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal
from typing import Literal


@dataclass(frozen=True, slots=True)
class FeePolicy:
    policy_id: str
    formula_version: Literal["quadratic-v1"]
    coefficient: Decimal
    multiplier: Decimal
    verified: bool


@dataclass(frozen=True, slots=True)
class FeeResult:
    status: Literal["verified", "estimated", "unavailable"]
    total_fee: Decimal | None
    assumptions: tuple[str, ...]
    unavailable_reason: str | None = None


def assess_fee(
    *,
    price: Decimal,
    quantity: int,
    participant_role: Literal["requester", "quoter", "unknown"],
    policy: FeePolicy | None,
) -> FeeResult:
    if not Decimal(0) <= price <= Decimal(1):
        raise ValueError("price must be between 0 and 1")
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    if participant_role == "unknown":
        return FeeResult(
            status="unavailable",
            total_fee=None,
            assumptions=(),
            unavailable_reason="RFQ participant role is unknown",
        )
    if policy is None:
        return FeeResult(
            status="unavailable",
            total_fee=None,
            assumptions=(),
            unavailable_reason="No applicable verified fee policy was supplied",
        )
    raw = policy.multiplier * policy.coefficient * Decimal(quantity) * price * (Decimal(1) - price)
    fee = raw.quantize(Decimal("0.000001"), rounding=ROUND_CEILING)
    status: Literal["verified", "estimated"] = "verified" if policy.verified else "estimated"
    assumptions = () if policy.verified else ("Fee policy is not independently verified.",)
    return FeeResult(status=status, total_fee=fee, assumptions=assumptions)
