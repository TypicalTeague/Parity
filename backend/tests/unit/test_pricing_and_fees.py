from decimal import Decimal

import pytest

from parity.domain.fees import FeePolicy, assess_fee
from parity.domain.pricing import net_expected_value, quote_difference


def test_quote_difference_uses_the_traders_side() -> None:
    fair, quote = Decimal("0.60"), Decimal("0.55")
    assert quote_difference(fair, quote, "buy") == Decimal("0.05")
    assert quote_difference(fair, quote, "sell") == Decimal("-0.05")


def test_net_expected_value_scales_quantity_and_subtracts_fee() -> None:
    assert net_expected_value(Decimal("0.05"), 10, Decimal("0.03")) == Decimal("0.47")


def test_unknown_role_fails_closed_instead_of_assuming_zero_fee() -> None:
    assessment = assess_fee(
        price=Decimal("0.55"), quantity=10, participant_role="unknown", policy=None
    )
    assert assessment.status == "unavailable"
    assert assessment.total_fee is None


def test_verified_policy_uses_decimal_ceiling_to_six_places() -> None:
    policy = FeePolicy(
        policy_id="test-only",
        formula_version="quadratic-v1",
        coefficient=Decimal("0.07"),
        multiplier=Decimal("1"),
        verified=True,
    )
    assessment = assess_fee(
        price=Decimal("0.55"), quantity=10, participant_role="requester", policy=policy
    )
    assert assessment.status == "verified"
    assert assessment.total_fee == Decimal("0.173250")


@pytest.mark.parametrize("price", [Decimal("-0.01"), Decimal("1.01")])
def test_fee_price_is_bounded(price: Decimal) -> None:
    policy = FeePolicy(
        policy_id="test-only",
        formula_version="quadratic-v1",
        coefficient=Decimal("0.07"),
        multiplier=Decimal("1"),
        verified=True,
    )
    with pytest.raises(ValueError, match="between 0 and 1"):
        assess_fee(price=price, quantity=1, participant_role="requester", policy=policy)
