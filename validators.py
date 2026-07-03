"""
validators.py
=============
Input validation utilities for order parameters.

All validators raise :class:`ValueError` with descriptive messages on
failure so that the caller (CLI or programmatic) can surface them cleanly
without leaking internal tracebacks.
"""

from typing import Optional

from bot.logging_config import logger

# ---------------------------------------------------------------------------
# Constants — accepted values
# ---------------------------------------------------------------------------
VALID_SIDES: frozenset[str] = frozenset({"BUY", "SELL"})
VALID_ORDER_TYPES: frozenset[str] = frozenset({"MARKET", "LIMIT"})


# ---------------------------------------------------------------------------
# Public validation functions
# ---------------------------------------------------------------------------


def validate_symbol(symbol: str) -> str:
    """
    Validate and normalise a trading symbol.

    Args:
        symbol (str): The raw symbol string provided by the user.

    Returns:
        str: The symbol converted to upper-case (e.g. ``"BTCUSDT"``).

    Raises:
        ValueError: If *symbol* is empty or contains only whitespace.
    """
    if not symbol or not symbol.strip():
        msg = "Symbol must not be empty."
        logger.warning("Validation failure — symbol: %s", msg)
        raise ValueError(msg)
    return symbol.strip().upper()


def validate_side(side: str) -> str:
    """
    Validate the order side.

    Args:
        side (str): Raw side string from the user (case-insensitive).

    Returns:
        str: Normalised side in upper-case (``"BUY"`` or ``"SELL"``).

    Raises:
        ValueError: If *side* is not one of the accepted values.
    """
    normalised = side.strip().upper()
    if normalised not in VALID_SIDES:
        msg = f"Side must be one of {sorted(VALID_SIDES)}. Received: '{side}'."
        logger.warning("Validation failure — side: %s", msg)
        raise ValueError(msg)
    return normalised


def validate_order_type(order_type: str) -> str:
    """
    Validate the order type.

    Args:
        order_type (str): Raw order type string (case-insensitive).

    Returns:
        str: Normalised order type in upper-case (``"MARKET"`` or ``"LIMIT"``).

    Raises:
        ValueError: If *order_type* is not one of the accepted values.
    """
    normalised = order_type.strip().upper()
    if normalised not in VALID_ORDER_TYPES:
        msg = (
            f"Order type must be one of {sorted(VALID_ORDER_TYPES)}. "
            f"Received: '{order_type}'."
        )
        logger.warning("Validation failure — order_type: %s", msg)
        raise ValueError(msg)
    return normalised


def validate_quantity(quantity: float) -> float:
    """
    Validate the order quantity.

    Args:
        quantity (float): The order quantity.

    Returns:
        float: The validated quantity.

    Raises:
        ValueError: If *quantity* is not strictly positive.
    """
    if quantity <= 0:
        msg = f"Quantity must be greater than 0. Received: {quantity}."
        logger.warning("Validation failure — quantity: %s", msg)
        raise ValueError(msg)
    return quantity


def validate_price(price: Optional[float], order_type: str) -> Optional[float]:
    """
    Validate the limit price, enforcing that it is required for LIMIT orders
    and must be positive when provided.

    Args:
        price (Optional[float]): The order price, or ``None`` for MARKET orders.
        order_type (str):        The normalised order type (``"MARKET"`` or ``"LIMIT"``).

    Returns:
        Optional[float]: The validated price, or ``None`` for MARKET orders.

    Raises:
        ValueError: If a LIMIT order is missing a price, or if the provided
                    price is not strictly positive.
    """
    if order_type == "LIMIT":
        if price is None:
            msg = "Price is required for LIMIT orders."
            logger.warning("Validation failure — price: %s", msg)
            raise ValueError(msg)
        if price <= 0:
            msg = f"Price must be greater than 0. Received: {price}."
            logger.warning("Validation failure — price: %s", msg)
            raise ValueError(msg)
    return price


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
) -> dict:
    """
    Run all validations in one call and return a dictionary of clean values.

    This is the primary entry point used by the CLI and order layer.

    Args:
        symbol (str):            Raw trading symbol.
        side (str):              Raw order side.
        order_type (str):        Raw order type.
        quantity (float):        Order quantity.
        price (Optional[float]): Limit price (``None`` for MARKET orders).

    Returns:
        dict: Cleaned and normalised parameters with keys:
              ``symbol``, ``side``, ``order_type``, ``quantity``, ``price``.

    Raises:
        ValueError: On the first validation failure encountered.
    """
    clean_symbol = validate_symbol(symbol)
    clean_side = validate_side(side)
    clean_type = validate_order_type(order_type)
    clean_qty = validate_quantity(quantity)
    clean_price = validate_price(price, clean_type)

    logger.debug(
        "Validation passed — symbol=%s side=%s type=%s qty=%s price=%s",
        clean_symbol,
        clean_side,
        clean_type,
        clean_qty,
        clean_price,
    )

    return {
        "symbol": clean_symbol,
        "side": clean_side,
        "order_type": clean_type,
        "quantity": clean_qty,
        "price": clean_price,
    }
