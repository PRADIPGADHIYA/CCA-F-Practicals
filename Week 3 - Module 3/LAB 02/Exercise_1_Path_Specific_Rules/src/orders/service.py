"""Order placement for NorthPeak."""

from __future__ import annotations

from decimal import Decimal

from auth.tokens import verify_token_v1  # TODO (Exercise 2): migrate to verify_token

CENTS = Decimal("0.01")


def place_order(token: str, items: list[dict]) -> dict:
    """Place an order if the caller's token is valid."""
    if not verify_token_v1(token):
        raise PermissionError("invalid token")
    subtotal = sum((Decimal(str(i["price"])) for i in items), Decimal("0")).quantize(CENTS)
    return {"placed": True, "item_count": len(items), "subtotal": subtotal}
