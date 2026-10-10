"""Decimal-safe quote and fee economics."""

from __future__ import annotations

from decimal import Decimal
from typing import Literal


def quote_difference(
    model_fair_value: Decimal,
    quoted_price: Decimal,
    intended_side: Literal["buy", "sell"],
) -> Decimal:
    """Return model-minus-quote for buys and quote-minus-model for sells."""
    difference = model_fair_value - quoted_price
    return difference if intended_side == "buy" else -difference


def net_expected_value(
    per_contract_quote_difference: Decimal,
    quantity: int,
    total_fee: Decimal,
) -> Decimal:
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    return per_contract_quote_difference * Decimal(quantity) - total_fee
